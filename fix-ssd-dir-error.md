# **How to Fix "Missing Privilege Separation Directory: /run/sshd" Error in SSH**

This error occurs when OpenSSH (`sshd`) cannot find the **privilege separation directory** (`/run/sshd`), which is required for security isolation. Here’s how to fix it:

---

## **1. Create the Missing Directory**
Run this command to create `/run/sshd`:
```bash
sudo mkdir -p /run/sshd
```
- `-p` ensures parent directories are created if needed.

---

## **2. Set Correct Permissions**
SSH requires strict permissions for security:
```bash
sudo chmod 0755 /run/sshd
sudo chown root:root /run/sshd
```

---

## **3. Restart SSH Service**
After creating the directory, restart `sshd`:
```bash
sudo systemctl restart ssh   # Ubuntu/Debian
sudo systemctl restart sshd  # Fedora/RHEL/CentOS
```

---

## **4. Verify SSH Starts Correctly**
Check the service status:
```bash
sudo systemctl status ssh
```
- If it fails, check logs:
  ```bash
  sudo journalctl -u ssh -xe --no-pager
  ```

---

## **5. Make the Fix Permanent (Systemd-Tmpfiles)**
Since `/run` is a `tmpfs` (temporary filesystem), the directory disappears on reboot. To recreate it automatically:

### **Option A: Use `systemd-tmpfiles` (Recommended)**
1. Create a config file:
   ```bash
   echo "d /run/sshd 0755 root root" | sudo tee /etc/tmpfiles.d/sshd.conf
   ```
2. Apply the change:
   ```bash
   sudo systemd-tmpfiles --create
   ```

### **Option B: Add to Startup Script (Alternative)**
Edit `/etc/rc.local` (create it if missing):
```bash
sudo nano /etc/rc.local
```
Add:
```bash
#!/bin/sh
mkdir -p /run/sshd
chmod 0755 /run/sshd
chown root:root /run/sshd
exit 0
```
Make it executable:
```bash
sudo chmod +x /etc/rc.local
```

---

## **6. Debug Manually (If Still Failing)**
Run `sshd` in debug mode to check for other issues:
```bash
sudo /usr/sbin/sshd -d
```
- Look for additional errors like missing config files or permissions issues.

---

## **7. Reinstall OpenSSH (Last Resort)**
If the issue persists, reinstall OpenSSH:
```bash
sudo apt purge openssh-server && sudo apt install openssh-server  # Ubuntu/Debian
sudo dnf reinstall openssh-server                               # Fedora/RHEL
```

---

### **Why This Happens**
- `/run/sshd` is a temporary directory cleared on reboot.
- System updates or incorrect service ordering may prevent its creation.
- Manual cleanup or misconfiguration removed the directory.

---

### **Prevent Future Issues**
- **Check `/run/sshd` after reboots**:
  ```bash
  ls -ld /run/sshd
  ```
- **Automate directory creation** (as in Step 5).

---

### **Final Fix Summary**
| Issue | Solution |
|-------|----------|
| **Missing `/run/sshd`** | `sudo mkdir -p /run/sshd` |
| **Permissions wrong** | `chmod 0755` + `chown root:root` |
| **Not persistent after reboot** | Use `systemd-tmpfiles` or `/etc/rc.local` |
| **Service still fails** | Check `journalctl -u ssh` |

After applying these fixes, SSH should start correctly. Let me know if you need further help! 🚀



----


### **How to Solve: "Disabling 'ssh.service', but its triggering units are still active: ssh.socket"**

This warning occurs when you try to disable `ssh.service` while `ssh.socket` is still active. **Socket activation** (`ssh.socket`) is an alternative way to start SSH on-demand when a connection is made, rather than running the service continuously.

---

## **Solution 1: Disable Both `ssh.service` and `ssh.socket`**
To fully disable SSH (if you don’t need it at all):
```bash
sudo systemctl disable --now ssh.service  # Disable & stop the service
sudo systemctl disable --now ssh.socket   # Disable & stop the socket
```

### **Verify:**
```bash
systemctl is-enabled ssh.service  # Should return "disabled"
systemctl is-enabled ssh.socket   # Should return "disabled"
```

---

## **Solution 2: Use Only `ssh.service` (Disable Socket Activation)**
If you want SSH to run as a **traditional service** (not on-demand via socket):
```bash
sudo systemctl disable --now ssh.socket    # Disable socket activation
sudo systemctl enable --now ssh.service    # Enable the standard service
```

### **Verify:**
```bash
systemctl is-active ssh.service  # Should be "active"
systemctl is-active ssh.socket   # Should be "inactive"
```

---

## **Solution 3: Use Only `ssh.socket` (On-Demand SSH)**
If you prefer **socket-based activation** (SSH starts only when a connection is made):
```bash
sudo systemctl disable --now ssh.service   # Disable the traditional service
sudo systemctl enable --now ssh.socket     # Enable socket activation
```

### **Verify:**
```bash
systemctl is-active ssh.socket    # Should be "active"
ss -ltnp | grep ssh              # Should show sshd listening on a socket
```

---

## **Why Does This Happen?**
- `ssh.socket` is an alternative to `ssh.service` (introduced in newer OpenSSH versions).
- Disabling `ssh.service` alone doesn’t stop `ssh.socket` from starting SSH when needed.
- Both must be disabled if you want SSH **completely turned off**.

---

## **Additional Troubleshooting**
### **1. Check Which Unit is Running SSH**
```bash
systemctl list-units | grep ssh
```
- If `ssh.socket` is active, it will start `ssh.service` dynamically.

### **2. Fully Stop SSH (Temporarily)**
```bash
sudo systemctl stop ssh.service ssh.socket
```

### **3. Re-enable SSH Later**
```bash
sudo systemctl enable --now ssh.service  # Traditional method
# OR
sudo systemctl enable --now ssh.socket   # On-demand method
```

---

## **Final Fix Summary**
| Goal | Command |
|------|---------|
| **Disable SSH completely** | `sudo systemctl disable --now ssh.service ssh.socket` |
| **Use traditional SSH (always running)** | `sudo systemctl disable --now ssh.socket && sudo systemctl enable --now ssh.service` |
| **Use on-demand SSH (socket activation)** | `sudo systemctl disable --now ssh.service && sudo systemctl enable --now ssh.socket` |

After applying these changes, the warning will disappear. Let me know if you need further help! 🚀
