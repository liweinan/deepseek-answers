# **How to Run `sshd` in Debug Mode**

Running `sshd` in debug mode helps troubleshoot connection issues, authentication problems, or configuration errors. Below are methods to start `sshd` in debug mode on Linux (Ubuntu, Fedora, etc.).

---

## **Method 1: Run `sshd` in Debug Mode (Foreground, Non-Daemon)**
This method runs `sshd` manually in the foreground with verbose logging.

### **1. Stop the Running SSH Service**
```bash
sudo systemctl stop ssh  # Ubuntu/Debian
sudo systemctl stop sshd # Fedora/RHEL
```

### **2. Start `sshd` in Debug Mode**
```bash
sudo /usr/sbin/sshd -d -p 2222
```
- `-d` → Debug mode (single level, use `-ddd` for maximum verbosity).
- `-p 2222` → Use a different port (optional, avoids conflict with the default SSH service).

### **3. Connect to Debug SSH Session**
From another terminal, connect using:
```bash
ssh -p 2222 user@localhost -vvv
```
- `-vvv` enables client-side debugging.

### **4. Stop Debug Mode**
Press `Ctrl+C` in the terminal running `sshd`.

---

## **Method 2: Run `sshd` with Full Debug Logging**
For deeper troubleshooting, use **`-D` (no forking)** + **`-e` (log to stderr)**:
```bash
sudo /usr/sbin/sshd -D -e -ddd -p 2222
```
- `-D` → Prevents `sshd` from detaching (runs in foreground).
- `-e` → Logs to `stderr` (visible in terminal).
- `-ddd` → Maximum verbosity.

---

## **Method 3: Debug Systemd-Managed `sshd`**
If you need to debug the actual system service:

### **1. Edit `sshd` Service File**
```bash
sudo systemctl edit --full ssh
```
(For Fedora/RHEL, use `sshd` instead of `ssh`.)

### **2. Modify `ExecStart`**
Replace the line with:
```ini
ExecStart=/usr/sbin/sshd -D -e -ddd $SSHD_OPTS
```
Save & exit (`Ctrl+X`, `Y`).

### **3. Reload & Restart SSH**
```bash
sudo systemctl daemon-reload
sudo systemctl restart ssh
```

### **4. View Debug Logs**
```bash
journalctl -u ssh -f
```
(For Fedora/RHEL, use `journalctl -u sshd -f`.)

---

## **Method 4: Log SSH Debug Output to a File**
To capture logs in a file:
```bash
sudo /usr/sbin/sshd -d -p 2222 -E /tmp/sshd-debug.log
```
- `-E /tmp/sshd-debug.log` → Logs output to a file.

---

## **Common Debugging Scenarios**
| Issue | Debug Command |
|--------|---------------|
| **Authentication failures** | `sshd -d -p 2222` + `ssh -vvv` |
| **Port binding issues** | `sshd -D -ddd -p 2222` |
| **Permission problems** | Check `/var/log/auth.log` (Ubuntu) or `/var/log/secure` (Fedora) |
| **SELinux blocking SSH** | `sudo ausearch -m avc -ts recent` |

---

## **Reverting Changes**
After debugging, restart the normal SSH service:
```bash
sudo systemctl start ssh  # Ubuntu
sudo systemctl start sshd # Fedora
```

---

### **Summary**
- **`sshd -d`** → Basic debug mode.
- **`sshd -D -e -ddd`** → Full debug logging.
- **`journalctl -u ssh -f`** → View systemd-managed SSH logs.
- **Port `2222`** → Avoids conflicts with the default SSH service.

This helps diagnose **connection drops, key authentication failures, or configuration errors**. Let me know if you need further help! 🔍