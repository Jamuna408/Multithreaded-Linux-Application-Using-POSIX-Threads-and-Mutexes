"""Multithreaded ATM & Bank Resource Management System (Python).
Every transaction runs in its own threading.Thread and takes a per-account mutex (threading.Lock).
Run:  pip install fastapi uvicorn   then   python app.py   ->  http://localhost:8080
"""
import os, random, secrets, sqlite3, threading, time
from collections import deque
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

HERE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()
G = threading.Lock()      # protects counters, log, timeline
dbl = threading.Lock()    # serialises SQLite access
db = sqlite3.connect(os.path.join(HERE, "bank_v2.db"), check_same_thread=False)

# ---------------- persistence ----------------
db.executescript("""create table if not exists acc(id int primary key,name,bal,init);
create table if not exists usr(u primary key,pw,pin,name,phone,branch,acct,pts default 0,loan default 0,emi default 0);
create table if not exists tx(id integer primary key autoincrement,acct,w,k,d,amt,bal);""")
if not db.execute("select 1 from acc").fetchone():
    db.executemany("insert into acc values(?,?,?,?)", [(i, n, b, b) for i, n, b in [
        (1001, "Moksha Ratna", 10000), (1002, "Chaitanya", 25000), (1003, "Anitha", 5000), (1004, "Ravi", 15000),
        (9001, "Race Lab A", 10000), (9002, "Race Lab B", 10000)]])
    db.executemany("insert into usr(u,pw,pin,name,phone,branch,acct) values(?,?,?,?,?,?,?)", [
        ("moksha", "pass123", "1111", "Moksha Ratna", "+91 98480 10001", "Hyderabad - Kukatpally", 1001),
        ("chaitanya", "pass123", "2222", "Chaitanya", "+91 98480 10002", "Hyderabad - Kukatpally", 1002),
        ("anitha", "pass123", "3333", "Anitha", "+91 98480 10003", "Hyderabad - Miyapur", 1003),
        ("ravi", "pass123", "4444", "Ravi", "+91 98480 10004", "Hyderabad - Miyapur", 1004)])
    db.commit()

def q(sql, *a):
    with dbl:
        db.execute(sql, a); db.commit()

class Acct:
    def __init__(s, i, n, b, init):
        s.id, s.name, s.bal, s.init, s.audit = i, n, b, init, b
        s.lock = threading.Lock()          # the mutex protecting this shared account
        s.owner = s.waiting = 0

A = {i: Acct(i, n, b, ini) for i, n, b, ini in db.execute("select id,name,bal,init from acc")}
U = {r[0]: dict(zip(("u", "pw", "pin", "name", "phone", "branch", "acct", "pts", "loan", "emi"), r), admin=0)
     for r in db.execute("select u,pw,pin,name,phone,branch,acct,pts,loan,emi from usr")}
TOK = {}
C = dict(sync=True, active=0, waiting=0, total=0, ok=0, rej=0, seq=0, tid=0)
D = dict(n=2, use=0, sem=threading.Semaphore(2))      # cash-dispenser channels (counting semaphore)
LOG, TL = deque(maxlen=60), deque(maxlen=30)

def usave(u): q("update usr set pin=?,pts=?,loan=?,emi=? where u=?", u["pin"], u["pts"], u["loan"], u["emi"], u["u"])
def allow(u, a): return a == u["acct"]
def err(m): return dict(ok=False, msg=m)
def jres(j): return dict(ok=j["ok"], atm=j["atm"], msg=j["msg"])

def log(j, k, m):
    with G:
        C["seq"] += 1; LOG.append(dict(t=time.strftime("%H:%M:%S"), tid=j["tid"] if j else 0, k=k, m=m))

def rec(x, k, amt, d):
    q("insert into tx(acct,w,k,d,amt,bal) values(?,?,?,?,?,?)", x.id, time.strftime("%d %b, %H:%M"), k, d, amt, x.bal)
    q("update acc set bal=? where id=?", x.bal, x.id)

def adj(x, d):
    with G: x.audit += d     # audit = sum of every approved change; must equal the balance

# ---------------- locking helpers ----------------
def lk(j, x):
    if not j["sync"]:
        j["acq"] = j["acq"] or time.time(); return True
    log(j, "wait", f"Thread {j['tid']} requests mutex on #{x.id}")
    with G: x.waiting += 1; C["waiting"] += 1
    ok = x.lock.acquire(timeout=j.get("timeout") or -1)      # blocks here if another thread holds it
    with G:
        x.waiting -= 1; C["waiting"] -= 1
        if ok: x.owner = j["atm"]
    if ok:
        j["acq"] = j["acq"] or time.time(); log(j, "lock", f"LOCK ACQUIRED on #{x.id}")
    return ok

def ul(j, x):
    if not j["sync"]: return
    with G: x.owner = 0
    x.lock.release(); log(j, "unlock", f"Mutex released on #{x.id}")

def dispense(j):
    log(j, "wait", f"Thread {j['tid']} waits for a dispenser channel (semaphore)")
    D["sem"].acquire()
    with G: D["use"] += 1
    log(j, "lock", f"Dispensing ₹{j['amt']} ({D['use']}/{D['n']} channels busy)")
    time.sleep(0.8)
    with G: D["use"] -= 1
    D["sem"].release(); log(j, "unlock", "Dispenser channel released")

# ---------------- the worker thread ----------------
NAMES = {"D": "deposit", "W": "withdraw", "T": "transfer", "B": "bill payment", "R": "loan EMI", "L": "credit"}

def work(j):
    t, amt = j["type"], j["amt"]
    a = A.get(j["frm"]); b = A.get(j["to"]) if t == "T" else None
    who = "Online" if j["atm"] == 3 else f"ATM {j['atm']}"
    held, j["req"], j["acq"] = [], time.time(), None
    with G: C["active"] += 1
    log(j, "info", f"{who} (thread {j['tid']}): {NAMES[t]} ₹{amt}" + ("" if j["sync"] else "  [NO MUTEX]"))
    rel = None
    try:
        if not a or amt <= 0 or (t == "T" and (not b or b is a)):
            j["msg"] = "Invalid account or amount"; log(j, "rej", j["msg"]); return
        order = [x for x in (a, b) if x]
        if not j.get("naive"): order.sort(key=lambda x: x.id)   # fixed lock order prevents deadlock
        for x in order:
            if not lk(j, x):
                j["msg"] = f"DEADLOCK: timed out waiting for #{x.id} while holding #{held[0].id}. Rolled back."
                log(j, "rej", j["msg"]); return
            held.append(x)
            if j.get("gap") and len(held) == 1: time.sleep(j["gap"])
        ba, bb = a.bal, (b.bal if b else 0)
        log(j, "crit", f"Critical section: read balance #{a.id} = ₹{ba}")
        time.sleep(j["hold"] / 1000)                       # simulated processing; widens the race window
        if t in "DL":
            a.bal = ba + amt; adj(a, amt); j["ok"] = True; rec(a, "Credit" if t == "L" else "Deposit", amt, j["d"])
        elif ba >= amt:
            a.bal = ba - amt; adj(a, -amt); j["ok"] = True
            rec(a, {"B": "Bill", "R": "Loan EMI", "T": "Transfer out"}.get(t, "Withdrawal"), -amt, j["d"])
            if b: b.bal = bb + amt; adj(b, amt); rec(b, "Transfer in", amt, j["d"])
        j["msg"] = f"{NAMES[t]} approved: ₹{amt}, balance ₹{a.bal}" if j["ok"] else f"REJECTED: insufficient balance (₹{a.bal})"
        log(j, "ok" if j["ok"] else "rej", j["msg"])
    finally:
        for x in reversed(held): ul(j, x)
        rel = time.time()
        with G:
            C["active"] -= 1; C["total"] += 1; C["ok" if j["ok"] else "rej"] += 1
            TL.append(dict(tid=j["tid"], atm=j["atm"], req=j["req"], acq=j["acq"] or rel, rel=rel, ok=j["ok"]))
    if t == "W" and j["ok"] and j.get("disp", True): dispense(j)

def job(u, **k):
    with G: C["tid"] += 1; tid = C["tid"]
    d = dict(atm=1, tid=tid, frm=0, to=0, amt=0, type="W", hold=1500, d="", user=u, sync=C["sync"], ok=False, msg="")
    d.update(k); return d

def run(*jobs, stagger=0.0):
    ths = []
    for j in jobs:
        th = threading.Thread(target=work, args=(j,)); th.start(); ths.append(th); time.sleep(stagger)
    for th in ths: th.join()          # controller waits for all workers

def reset(labs_only=False):
    for x in A.values():
        if labs_only and x.id < 9000: continue
        x.bal = x.audit = x.init; q("update acc set bal=? where id=?", x.init, x.id)
    if not labs_only:
        q("delete from tx")
        for u in U.values(): u["pts"] = u["loan"] = u["emi"] = 0; usave(u)
        with G: LOG.clear(); TL.clear(); C.update(active=0, waiting=0, total=0, ok=0, rej=0, seq=0)

# ---------------- API ----------------
class Auth(Exception): pass
@app.exception_handler(Auth)
def _auth(request, exc): return JSONResponse({"err": "auth"})
def user(tok: str = ""):
    if tok not in TOK: raise Auth()
    return TOK[tok]
def route(p): return app.api_route(p, methods=["GET", "POST"])

@app.get("/")
def index(): return FileResponse(os.path.join(HERE, "index.html"))

@route("/api/login")
def login(u: str = "", p: str = ""):
    x = U.get(u.strip().lower())
    if not x or x["pw"] != p: return err("Wrong username or password")
    t = secrets.token_hex(8); TOK[t] = x; return dict(ok=True, tok=t)

@route("/api/register")
def register(u: str = "", pw: str = "", pin: str = "", name: str = ""):
    u = u.strip().lower()
    if not (3 <= len(u) <= 12 and u.isalnum()): return err("Username must be 3 to 12 letters or digits")
    if len(pw) < 4: return err("Password must be at least 4 characters")
    if not (len(pin) == 4 and pin.isdigit()): return err("PIN must be exactly 4 digits")
    with G:
        if u in U: return err("That username is taken")
        acct = max(i for i in A if i < 9000) + 1; nm = name.strip()[:24] or u.title()
        A[acct] = Acct(acct, nm, 10000, 10000)
        x = U[u] = dict(u=u, pw=pw, pin=pin, name=nm, phone="+91 90000 00000", branch="Hyderabad - Kukatpally", acct=acct, pts=0, loan=0, emi=0, admin=0)
    q("insert into acc values(?,?,?,?)", acct, nm, 10000, 10000)
    q("insert into usr(u,pw,pin,name,phone,branch,acct) values(?,?,?,?,?,?,?)", u, pw, pin, nm, x["phone"], x["branch"], acct)
    t = secrets.token_hex(8); TOK[t] = x; return dict(ok=True, tok=t)

@route("/api/logout")
def logout(tok: str = ""): TOK.pop(tok, None); return {}

@route("/api/state")
def state(u=Depends(user)):
    with G:
        d = dict(sync=C["sync"], active=C["active"], waiting=C["waiting"], total=C["total"], ok=C["ok"], rej=C["rej"], seq=C["seq"],
                 me=dict(u=u["u"], name=u["name"], phone=u["phone"], branch=u["branch"], acct=u["acct"], admin=0, pts=u["pts"], loan=u["loan"], emi=u["emi"]),
                 accounts=[dict(id=x.id, name=x.name, bal=x.bal, audit=x.audit, owner=x.owner, waiting=x.waiting) for x in A.values()],
                 log=list(LOG)[-40:], disp=dict(n=D["n"], use=D["use"]))
        d["tl"] = list(TL)[-10:]
    return d

@route("/api/txs")
def txs(u=Depends(user)):
    with dbl: rows = db.execute("select acct,w,k,amt,bal,d from tx order by id desc limit 400").fetchall()
    return dict(t=[dict(a=a, w=w, k=k, amt=m, bal=b, d=d) for a, w, k, m, b, d in rows if allow(u, a)][:60])

@route("/api/tx")
def tx(atm: int = 1, type: str = "withdraw", acct: int = 0, to: int = 0, amount: int = 0, hold: int = 1500, pin: str = "", u=Depends(user)):
    t = (type[:1].upper() or "W"); t = t if t in "WDT" else "W"
    if not allow(u, acct): return err("You can only use your own account")
    if u["pin"] != pin: return err("Incorrect PIN")
    j = job(u, atm=atm, frm=acct, to=to, amt=amount, type=t, hold=min(hold, 8000), d=f"ATM {atm}"); run(j)
    if j["ok"] and t == "T":
        with G: u["pts"] += amount // 100
        usave(u)
    return jres(j)

@route("/api/bill")
def bill(name: str = "", amount: int = 0, acct: int = 0, hold: int = 700, pin: str = "", u=Depends(user)):
    if not allow(u, acct): return err("You can only use your own account")
    if u["pin"] != pin: return err("Incorrect PIN")
    j = job(u, atm=3, frm=acct, amt=amount, type="B", hold=min(hold, 8000), d=f"Bill: {name[:24]}"); run(j)
    if j["ok"]:
        with G: u["pts"] += amount // 100
        usave(u)
    return jres(j)

@route("/api/loan")
def loan(amount: int = 0, u=Depends(user)):
    if not 10000 <= amount <= 100000: return err("Choose an amount between 10,000 and 1,00,000")
    with G:
        if u["loan"]: return err("Repay your current loan first")
        u["loan"] = -1                                   # reserve the slot so two requests cannot both pass
    j = job(u, atm=3, frm=u["acct"], amt=amount, hold=600, type="L", d="Loan disbursed", disp=False); run(j)
    with G:
        u["loan"] = amount * 110 // 100 if j["ok"] else 0
        u["emi"] = -(-u["loan"] // 6) if j["ok"] else 0
    usave(u); return jres(j)

@route("/api/emi")
def emi(u=Depends(user)):
    amt = min(u["loan"], u["emi"])
    if amt <= 0: return err("You have no active loan")
    j = job(u, atm=3, frm=u["acct"], amt=amt, hold=600, type="R", d="Loan EMI"); run(j)
    if j["ok"]:
        with G:
            u["loan"] -= amt
            if u["loan"] <= 0: u["loan"] = u["emi"] = 0
        usave(u)
    return jres(j)

@route("/api/redeem")
def redeem(r: int = -1, u=Depends(user)):
    cost, cash = (100, 450, 800), (50, 250, 500)
    if not 0 <= r <= 2: return err("Reward not available")
    with G:
        if u["pts"] < cost[r]: return err("Not enough reward points")
        u["pts"] -= cost[r]                              # deduct first so double-clicks cannot double-spend
    j = job(u, atm=3, frm=u["acct"], amt=cash[r], hold=400, type="L", d="Rewards cashback", disp=False); run(j)
    if not j["ok"]:
        with G: u["pts"] += cost[r]
    usave(u); return jres(j)

@route("/api/pin")
def pin(old: str = "", new: str = "", u=Depends(user)):
    if u["pin"] != old: return err("Current PIN is wrong")
    if not (len(new) == 4 and new.isdigit()): return err("New PIN must be exactly 4 digits")
    u["pin"] = new; usave(u); return dict(ok=True, msg="PIN changed")

# ---------------- admin: OS labs ----------------
@route("/api/race")
def race(acct: int = 1001, a: int = 7000, b: int = 5000, hold: int = 2500, u=Depends(user)):
    j1, j2 = (job(u, atm=n, frm=acct, amt=m, hold=min(hold, 8000), d=f"ATM {n}") for n, m in ((1, a), (2, b)))
    run(j1, j2, stagger=0.04)
    return dict(r=[dict(atm=j["atm"], ok=j["ok"], msg=j["msg"]) for j in (j1, j2)])

@route("/api/sync")
def sync(on: int = 1, u=Depends(user)):
    C["sync"] = bool(on); log(None, "info", "Mutex synchronization " + ("ENABLED" if on else "DISABLED (race conditions possible)")); return {}

@route("/api/reset")
def reset_all(u=Depends(user)):
    reset(); return {}

@route("/api/compare")
def compare(hold: int = 1500, u=Depends(user)):
    out = {}
    for mode in (True, False):
        reset(True)
        j1, j2 = (job(u, atm=n, frm=9001, amt=m, hold=hold, sync=mode, disp=False) for n, m in ((1, 7000), (2, 5000)))
        run(j1, j2, stagger=0.04); x = A[9001]
        out["on" if mode else "off"] = dict(bal=x.bal, audit=x.audit, msgs=[j1["msg"], j2["msg"]])
    reset(True); return out

@route("/api/deadlock")
def deadlock(ordered: int = 0, u=Depends(user)):
    reset(True)
    kw = dict(amt=100, type="T", hold=300, gap=1.0, naive=not ordered, timeout=3, sync=True, disp=False)
    j1, j2 = job(u, atm=1, frm=9001, to=9002, **kw), job(u, atm=2, frm=9002, to=9001, **kw)
    run(j1, j2, stagger=0.05)
    return dict(msgs=[j1["msg"], j2["msg"]])

@route("/api/stress")
def stress(n: int = 30, sync: int = 1, u=Depends(user)):
    reset(True)
    js = [job(u, atm=random.randint(1, 2), frm=(f := random.choice((9001, 9002))), to=(9002 if f == 9001 else 9001),
              amt=random.choice((100, 200, 300, 500)), type=random.choice("WDT"), hold=15, sync=bool(sync), disp=False)
          for _ in range(min(n, 100))]
    run(*js, stagger=0.002)
    acc = [dict(id=x.id, bal=x.bal, audit=x.audit) for x in (A[9001], A[9002])]
    return dict(n=len(js), ok=sum(j["ok"] for j in js), rej=sum(not j["ok"] for j in js), accounts=acc,
                consistent=all(a["bal"] == a["audit"] for a in acc))

@route("/api/config")
def config(channels: int = 2, u=Depends(user)):
    if D["use"]: return err("Dispenser is busy. Try again in a moment")
    D["n"] = max(1, min(channels, 5)); D["sem"] = threading.Semaphore(D["n"])
    return dict(ok=True, msg=f"Dispenser now has {D['n']} channel(s)")

if __name__ == "__main__":
    print("ATM system running -> http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
