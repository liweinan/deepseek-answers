# Setting Up Golang Bin Path in Fish Shell

To properly set up your Go binary path in Fish shell, follow these steps:

## 1. First, Verify Your Go Installation

Check if Go is installed and where it's installed:
```fish
which go
```

This should show something like `/usr/local/go/bin/go` or `$HOME/go/bin/go`

## 2. Add Go to Your Fish Shell Path

Edit your Fish config file:
```fish
nano ~/.config/fish/config.fish
```

Add these lines (adjust paths according to your installation):

```fish
# Set GOPATH if you use it (optional for Go 1.11+)
set -x GOPATH $HOME/go

# Add Go binary directory to PATH
set -x PATH $PATH /usr/local/go/bin

# Add GOPATH/bin to PATH for installed Go tools
set -x PATH $PATH $GOPATH/bin
```

## 3. Reload Your Fish Shell

Apply the changes:
```fish
source ~/.config/fish/config.fish
```

## 4. Verify the Setup

Check your Go environment:
```fish
go env
```

Verify the PATH contains Go binaries:
```fish
echo $PATH
```

## Alternative: Using Fish's `fish_add_path`

For Fish 3.2+ (recommended cleaner approach):
```fish
# Add these to config.fish
fish_add_path /usr/local/go/bin
fish_add_path $HOME/go/bin
```

## Additional Useful Go Fish Shell Settings

You might want to add these to your config.fish:

```fish
# For Go modules
set -x GO111MODULE on

# For private repositories
set -x GOPRIVATE "github.com/yourname/*"

# For faster builds
set -x GOMODCACHE $HOME/go/pkg/mod
```

## Troubleshooting

If things don't work:
1. Verify Go installation path:
   ```fish
   ls /usr/local/go/bin/go
   ```

2. Check if PATH is being set correctly:
   ```fish
   echo $PATH | tr ' ' '\n' | grep go
   ```

3. For custom installations, adjust paths accordingly.

Remember that Fish shell syntax is different from Bash, so don't use `export VAR=value` - use `set -x VAR value` instead.