# VaultThreads: Multithreaded ATM & Bank Resource Management System

An Operating Systems project that shows how concurrent ATM transactions are kept safe with **threads and mutex locks**.
Every banking operation runs in its own thread. A per-account mutex protects the shared balance, so two ATMs withdrawing from the
same account at the same time cannot corrupt it. A web dashboard lets you watch the threads, locks and balances live.

## OS concepts demonstrated

| Concept | Where it appears |
|---|---|
| Threads | Each withdraw, deposit, transfer, bill payment and loan request runs in its own `threading.Thread` |
| Shared resources | Account balances and the transaction ledger |
| Mutex locks | One `threading.Lock` per account protects the balance |
| Critical section | Read balance, check, then write balance |
| Race condition | Switch the mutex off and run two simultaneous withdrawals |
| Synchronization | Waiting threads block until the mutex is released |
| Thread joining | The controller calls `join()` on every worker before replying |
| Deadlock | OS Labs: naive vs ordered lock acquisition, with timeout-based recovery |
| Semaphore | A counting semaphore limits the cash-dispenser channels |
| Audit check | An independent audit total proves when a balance is corrupted |

## Features

- Login and account creation, with a separate 4-digit PIN that is asked again for every withdraw, deposit, transfer and bill payment
- Dashboard with live mutex status per account (FREE / LOCKED / WAITING), thread counters and a SAFE / UNSAFE mutex switch
- One-click race demo: ₹7,000 and ₹5,000 withdrawn at once from a ₹10,000 account
- ATM terminals, transaction history (with CSV export), bill payments, loans with EMI, and reward points with cashback
- OS Labs: thread timeline, mutex on/off comparison, deadlock demo, stress test and dispenser semaphore
- SQLite persistence, so balances and history survive restarts

## Run it

Requires Python 3.9 or newer.

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080

## Demo logins

| Username | Password | PIN | Account |
|---|---|---|---|
| moksha | pass123 | 1111 | 1001 |
| chaitanya | pass123 | 2222 | 1002 |
| anitha | pass123 | 3333 | 1003 |
| ravi | pass123 | 4444 | 1004 |

You can also create your own account from the login page.

## Demonstrate the race condition

1. Sign in and open the Dashboard, then click **Reset**.
2. With the pill showing **SAFE (mutex ON)**, click **Run race demo**. ATM 1 succeeds, ATM 2 is rejected, and the balance is ₹3,000.
3. Click the pill to switch to **UNSAFE (mutex OFF)**, click **Reset**, then run the demo again. Both withdrawals succeed and the balance is wrong.
4. Switch the mutex back on and click **Reset**.

## Project structure

```
app.py            FastAPI backend: threads, mutexes, semaphore, SQLite, REST API
index.html        Single-page dashboard served by the backend
requirements.txt  Python dependencies
```

## Notes

- Passwords and PINs are stored in plain text. This is a classroom demo, not a real banking system.
- Python's `threading` module uses the operating system's native threads and mutexes.
- The OS Labs experiments use two separate Race Lab accounts, so customer balances are never touched.
