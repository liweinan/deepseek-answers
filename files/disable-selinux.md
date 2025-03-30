# Disable SELinux On Ubuntu

Ubuntu does **not** use SELinux by default—it uses **AppArmor** instead. However, if SELinux was manually installed or enabled, here’s how to disable it:

---

### **1. Check if SELinux is Installed**
Run:
```bash
sudo apt list --installed | grep selinux
```
- If no output, **SELinux is not installed** (Ubuntu uses AppArmor).
- If packages like `selinux-basics`, `selinux-utils`, or `policycoreutils` appear, proceed below.

---

### **2. Temporarily Set SELinux to Permissive Mode**
(For testing before full disablement)
```bash
sudo setenforce 0
```
- This makes SELinux log violations but not enforce them.
- Verify status:
  ```bash
  getenforce
  ```
  (Should return `Permissive`).

---

### **3. Permanently Disable SELinux**
Edit the SELinux config file:
```bash
sudo nano /etc/selinux/config
```
Change the line:
```ini
SELINUX=enforcing
```
to:
```ini
SELINUX=disabled
```
Save (`Ctrl+X` → `Y` → `Enter`), then **reboot**:
```bash
sudo reboot
```

---

### **4. Verify SELinux is Disabled**
After reboot, run:
```bash
sestatus
```
- Expected output:
  ```bash
  SELinux status:       disabled
  ```

---

### **5. (Optional) Remove SELinux Packages**
To completely uninstall SELinux:
```bash
sudo apt purge selinux-basics selinux-utils policycoreutils
sudo apt autoremove
```

---

### **Important Notes**
1. **AppArmor ≠ SELinux**  
   Ubuntu’s default security module is AppArmor. Disable it separately if needed:
   ```bash
   sudo systemctl disable apparmor --now
   ```
2. **Security Impact**  
   Disabling SELinux/AppArmor reduces security. Only do this if necessary (e.g., for compatibility).

---

### **Troubleshooting**
- **"Command not found" errors?** SELinux isn’t installed (normal for Ubuntu).
- **Need to switch to AppArmor?**  
  Enable it with:
  ```bash
  sudo systemctl enable apparmor --now
  ```

Let me know if you need further help! 🔧