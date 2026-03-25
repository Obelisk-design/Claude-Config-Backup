# TODOs

> Tracked improvements and deferred work for the Claude Config Backup project.

---

## SSH Storage Improvements

### TODO-001: Extract SSH Storage Helper Function

**What:** Create a helper function `_get_ssh_storage(config)` that handles password decryption and SSHStorage instantiation.

**Why:** The pattern is repeated 6 times across 4 files. A helper would reduce duplication and ensure consistency.

**Pros:**
- DRY principle
- Easier to maintain
- Single source of truth for SSH instantiation

**Cons:**
- Adds one more file
- Minor refactoring effort

**Context:**
Files affected: `backup_tab.py`, `restore_tab.py`, `history_tab.py` (x4 occurrences).
Pattern to extract:
```python
crypto = Crypto()
password = crypto.decrypt(password_encrypted)
storage = SSHStorage(host=..., port=..., user=..., password=password)
```

**Effort:** S (human: ~30 min / CC: ~5 min)
**Priority:** P2
**Status:** DONE
**Created:** 2026-03-25
**Completed:** 2026-03-25
**Depends on:** None

---

### TODO-002: Add Retry Logic Test

**What:** Add unit tests for `SSHStorage._connect()` retry logic.

**Why:** The retry logic (3 attempts with linear backoff 2s/4s/6s) is not tested. A test would verify the retry behavior works correctly.

**Pros:**
- Complete test coverage
- Confidence in retry behavior
- Catches regressions

**Cons:**
- Requires mocking SSHClient with side effects
- Slightly more complex test setup

**Context:**
`tests/test_ssh_storage.py` needs two new tests:
1. `test_connect_retry_success` — mock SSHClient to fail twice then succeed
2. `test_connect_retry_exhausted` — mock SSHClient to fail all 3 times

**Effort:** S (human: ~30 min / CC: ~5 min)
**Priority:** P2
**Status:** DONE
**Created:** 2026-03-25
**Completed:** 2026-03-25
**Depends on:** None

---

### TODO-003: Map SSH Errors to User-Friendly Messages

**What:** Create an error message mapping function that translates technical SSH errors to user-friendly Chinese messages.

**Why:** Users see raw exception messages like `SSH connection failed after 3 retries: [Errno 111] Connection refused`. Power users understand this, but regular users may be confused.

**Pros:**
- Better user experience
- Clearer error resolution guidance
- Professional feel

**Cons:**
- Requires maintaining error mapping
- May not cover all edge cases

**Context:**
Common errors to map:
- `Authentication failed` → `用户名或密码错误，请检查凭据`
- `Connection refused` → `无法连接到服务器，请检查地址和端口`
- `Network unreachable` → `网络不可达，请检查网络连接`
- `Host key verification failed` → `服务器密钥验证失败`
- `Timeout` → `连接超时，请检查服务器状态`

Location: Add to `src/storage/ssh_storage.py` or create `src/utils/error_messages.py`

**Effort:** S (human: ~30 min / CC: ~5 min)
**Priority:** P2
**Status:** DONE
**Created:** 2026-03-25
**Completed:** 2026-03-25
**Depends on:** None