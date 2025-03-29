# Enable SSH login on Ubuntu

To enable SSH login on Ubuntu, you'll need to install and configure the OpenSSH server (`sshd`). Here’s a step-by-step guide:

---

### **Step 1: Install OpenSSH Server**
Update your package list and install the SSH server:
```bash
sudo apt update
sudo apt install openssh-server
```

---

### **Step 2: Check SSH Service Status**
The SSH service should start automatically. Verify it’s running:
```bash
sudo systemctl status ssh
```
- If it’s not running, start it manually:
  ```bash
  sudo systemctl start ssh
  ```
- Enable SSH to start at boot (optional):
  ```bash
  sudo systemctl enable ssh
  ```

---

### **Step 3: Allow SSH Through the Firewall**
If you’re using **UFW** (Ubuntu’s firewall), allow SSH (port 22):
```bash
sudo ufw allow ssh
```
Or explicitly allow port 22:
```bash
sudo ufw allow 22/tcp
```
Check UFW status:
```bash
sudo ufw status
```

---

### **Step 4: Find Your Server’s IP Address**
To connect, you’ll need the server’s IP. Run:
```bash
ip a
```
Look for `inet` under your active network interface (e.g., `eth0` or `wlan0`).

---

### **Step 5: Connect to SSH from Another Machine**
From a remote machine (Linux/macOS), use:
```bash
ssh username@your_server_ip
```
- Replace `username` with your Ubuntu username.
- Replace `your_server_ip` with the server’s actual IP.

On **Windows**, use **PuTTY** or **Windows Terminal** with the same command.

---

### **Step 6: (Optional) Configure SSH for Security**
Edit the SSH config file to improve security:
```bash
sudo nano /etc/ssh/sshd_config
```
Recommended changes:
```ini
Port 2222                      # Change default port (optional)
PermitRootLogin no             # Disable root login
PasswordAuthentication no      # Disable password auth (use keys only)
```
Save (`Ctrl+X` → `Y` → `Enter`) and restart SSH:
```bash
sudo systemctl restart ssh
```
If you changed the port, update the firewall:
```bash
sudo ufw allow 2222/tcp
```

---

### **Step 7: (Optional) Set Up SSH Key Authentication**
For passwordless, more secure logins:
1. **Generate a key pair** (on your local machine):
   ```bash
   ssh-keygen -t ed25519
   ```
2. **Copy the public key** to the server:
   ```bash
   ssh-copy-id username@your_server_ip
   ```
3. **Test login** (should not prompt for a password):
   ```bash
   ssh username@your_server_ip
   ```

---

### **Troubleshooting**
- **"Connection refused"**: Ensure SSH is running (`sudo systemctl status ssh`).
- **Firewall blocking access?** Check `sudo ufw status`.
- **Permission issues?** Ensure `~/.ssh/authorized_keys` has `600` permissions:
  ```bash
  chmod 600 ~/.ssh/authorized_keys
  ```

---

### **Summary**
1. Install `openssh-server`.
2. Start and enable the `ssh` service.
3. Allow SSH in the firewall (`sudo ufw allow ssh`).
4. Connect using `ssh username@ip`.
5. (Optional) Harden SSH by disabling passwords and changing the port.

Let me know if you need further help! 🚀
