# Installing Stockfish

## Ubuntu/Debian (WSL):
```bash
sudo apt update
sudo apt install stockfish
```

## Verify installation:
```bash
stockfish
# Should display "Stockfish XX by Tord Romstad..."
# Type "quit" to exit
```

## Alternative - Download binary:
1. Go to https://stockfishchess.org/download/
2. Download for Linux
3. Extract and copy to /usr/local/bin/

## After installing:
```bash
python chess.py
```

The "Engine" button will automatically enable when Stockfish is available.