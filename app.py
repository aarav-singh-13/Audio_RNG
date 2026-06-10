import string
import argparse
from audio_rng import AudioRNG

def generate_password(rng, length=16, use_uppercase=True, use_numbers=True, use_symbols=True):
    # Build the character pool
    pool = string.ascii_lowercase
    if use_uppercase:
        pool += string.ascii_uppercase
    if use_numbers:
        pool += string.digits
    if use_symbols:
        pool += string.punctuation
        
    if not pool:
        raise ValueError("At least one character set must be selected.")

    # Generate the password
    password = "".join(rng.choice(pool) for _ in range(length))
    return password

def main():
    parser = argparse.ArgumentParser(description="Audio-Based Secure Password Generator")
    parser.add_argument("-l", "--length", type=int, default=16, help="Length of the password (default: 16)")
    parser.add_argument("--no-upper", action="store_true", help="Exclude uppercase letters")
    parser.add_argument("--no-numbers", action="store_true", help="Exclude numbers")
    parser.add_argument("--no-symbols", action="store_true", help="Exclude symbols")
    
    args = parser.parse_args()
    
    print("=== True Random Password Generator ===")
    print("Initializing Audio RNG...")
    # Initialize the generator (captures 1 second of audio)
    rng = AudioRNG(duration=1.0)
    
    try:
        password = generate_password(
            rng, 
            length=args.length,
            use_uppercase=not args.no_upper,
            use_numbers=not args.no_numbers,
            use_symbols=not args.no_symbols
        )
        print("\n[SUCCESS] Password Generated:")
        print("-" * 40)
        print(password)
        print("-" * 40)
    except Exception as e:
        print(f"\n[ERROR] Failed to generate password: {e}")

if __name__ == "__main__":
    main()
