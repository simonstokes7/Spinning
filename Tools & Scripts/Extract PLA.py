import sys
import struct
from pathlib import Path

def analyze_pla_binary(pla_file_path):
    pla_path = Path(pla_file_path)
    if not pla_path.exists():
        print(f"Error: Could not find '{pla_path}'")
        return

    size = pla_path.stat().st_size
    print(f"File Size: {size} bytes")

    if size == 0:
        print("Diagnosis: The file is completely empty (0 bytes).")
        return

    with open(pla_path, 'rb') as f:
        data = f.read(128) # Read up to first 128 bytes for hex dump

    # 1. Hex Dump
    print("\n--- Raw Hex Dump (First 128 bytes) ---")
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = " ".join(f"{b:02X}" for b in chunk)
        text_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        print(f"{i:04X}  {hex_str:<48}  {text_str}")

    # 2. Check for MTP Object ID Array (32-bit integers)
    if len(data) >= 4:
        print("\n--- MTP Database ID Check ---")
        with open(pla_path, 'rb') as f:
            full_data = f.read()
        
        # Unpack as little-endian unsigned integers
        int_count = len(full_data) // 4
        if int_count > 0:
            try:
                ints = struct.unpack(f"<{int_count}I", full_data[:int_count*4])
                print(f"Total 32-bit integers found: {len(ints)}")
                print(f"First 10 integers: {ints[:10]}")
                print("\nDiagnosis:")
                if all(i == 0 for i in ints):
                    print("The file contains only zeroes. The playlist is empty or corrupted.")
                else:
                    print("If the integers above are random numbers (e.g., 5, 23, 1045), this file stores MTP database IDs.")
                    print("You cannot extract track names from this file because they don't exist here. They lived in the device's database.")
            except Exception as e:
                print(f"Could not parse as integers: {e}")

if __name__ == "__main__":
    # Ensure this points to your specific .pla file
    target_file = sys.argv[1] if len(sys.argv) > 1 else "playlist.pla"
    analyze_pla_binary(target_file)