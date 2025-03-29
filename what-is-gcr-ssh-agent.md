# **What is `gcr-ssh-agent`?**

`gcr-ssh-agent` is a component of the **GNOME Keyring** (`gnome-keyring`) system, which manages SSH keys, GPG keys, and passwords in GNOME-based Linux environments (like Ubuntu's default desktop). It acts as an alternative to the default `ssh-agent`, automatically loading SSH keys stored in GNOME Keyring when you log in.

#### **Key Features:**
- Stores SSH keys securely in GNOME Keyring.
- Unlocks keys using your login password.
- Runs automatically in GNOME sessions.

---

### **How to Disable `gcr-ssh-agent` on Ubuntu**

#### **Method 1: Disable for Current User (Temporary)**
1. **Stop the running `gcr-ssh-agent`:**
   ```bash
   killall gcr-ssh-agent
   ```
2. **Prevent it from auto-starting in your session:**
   ```bash
   mv ~/.config/autostart/gnome-keyring-ssh.desktop ~/.config/autostart/gnome-keyring-ssh.desktop.bak
   ```
3. **Log out and back in** for changes to take effect.

---

#### **Method 2: Disable System-Wide (Permanent)**
1. **Mask the GNOME Keyring SSH agent service:**
   ```bash
   systemctl --user mask gnome-keyring-ssh.socket
   ```
2. **Stop any running instances:**
   ```bash
   systemctl --user stop gnome-keyring-ssh.service
   ```
3. **Use the default `ssh-agent` instead:**
   Add this to `~/.bashrc` or `~/.zshrc`:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_rsa  # Or your key path
   ```
4. **Restart your session** (log out and back in).

---

#### **Method 3: Remove GNOME Keyring (Not Recommended)**
If you don’t need GNOME Keyring at all:
```bash
sudo apt remove gnome-keyring
```
⚠️ **Warning:** This may affect other GNOME features (e.g., Wi-Fi passwords, encrypted storage).

---

### **Verify `gcr-ssh-agent` is Disabled**
1. Check running processes:
   ```bash
   ps aux | grep gcr-ssh-agent
   ```
   (No output means it's stopped.)
2. Test SSH:
   ```bash
   ssh -T git@github.com  # Example
   ```
   If it no longer auto-unlocks keys, `gcr-ssh-agent` is disabled.

---

### **Why Disable It?**
- You prefer the standard `ssh-agent`.
- Conflicts with other tools (e.g., `GPG agent` for SSH).
- You use a non-GNOME desktop environment.

---

### **Revert Changes**
To re-enable `gcr-ssh-agent`:
```bash
systemctl --user unmask gnome-keyring-ssh.socket
systemctl --user start gnome-keyring-ssh.service
mv ~/.config/autostart/gnome-keyring-ssh.desktop.bak ~/.config/autostart/gnome-keyring-ssh.desktop
```

Let me know if you need further help! 🔧