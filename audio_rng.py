import sounddevice as sd
import numpy as np
import hashlib
import time

class AudioRNG:
    def __init__(self, sample_rate=44100, duration=1.0):
        self.sample_rate = sample_rate
        self.duration = duration
        self._seed = None
        self._counter = 0

    def _capture_audio_entropy(self):
        """Captures live audio from the microphone and returns a cryptographic hash."""
        print(f"[*] Capturing {self.duration}s of audio from microphone for entropy...")
        # Record audio
        recording = sd.rec(int(self.duration * self.sample_rate), 
                           samplerate=self.sample_rate, 
                           channels=1, 
                           dtype='float32')
        sd.wait()  # Wait until recording is finished
        
        # Convert to bytes
        raw_bytes = recording.tobytes()
        
        # Add system time as extra salt (doesn't hurt, adds a bit more unpredictability)
        salt = str(time.time()).encode()
        
        # Hash the raw audio data + salt using SHA-512 to distill the entropy
        hasher = hashlib.sha512()
        hasher.update(raw_bytes)
        hasher.update(salt)
        
        return hasher.digest()

    def _reseed(self):
        self._seed = self._capture_audio_entropy()
        self._counter = 0

    def get_random_bytes(self, num_bytes):
        """Generates cryptographically secure random bytes based on the audio seed."""
        if self._seed is None:
            self._reseed()
            
        result = b""
        while len(result) < num_bytes:
            # Hash the seed with a counter to generate a stream of random bytes
            hasher = hashlib.sha512()
            hasher.update(self._seed)
            hasher.update(self._counter.to_bytes(8, byteorder='big'))
            
            chunk = hasher.digest()
            result += chunk
            self._counter += 1
            
            # Reseed after a certain number of uses to maintain high entropy
            if self._counter > 1000:
                self._reseed()
                
        return result[:num_bytes]

    def choice(self, seq):
        """Choose a random element from a non-empty sequence."""
        if not seq:
            raise IndexError("Cannot choose from an empty sequence")
            
        # We need to map our random bytes to an index.
        # To avoid modulo bias, we'll use rejection sampling or a large enough byte range.
        # For simplicity, we get 4 bytes (32-bit int) and use modulo if the bias is negligible.
        # Since sequences for passwords are small (< 100), 2**32 is huge, modulo bias is practically zero.
        rand_bytes = self.get_random_bytes(4)
        rand_int = int.from_bytes(rand_bytes, byteorder='big')
        return seq[rand_int % len(seq)]

    def get_random_int(self, min_val, max_val):
        """Return a random integer N such that min_val <= N <= max_val."""
        if min_val > max_val:
            raise ValueError("min_val must be <= max_val")
        range_size = max_val - min_val + 1
        
        # Determine how many bytes we need to represent the range
        num_bytes = (range_size.bit_length() + 7) // 8
        if num_bytes == 0:
            return min_val
            
        # Rejection sampling to ensure perfectly uniform distribution
        while True:
            rand_bytes = self.get_random_bytes(num_bytes)
            rand_int = int.from_bytes(rand_bytes, byteorder='big')
            if rand_int < (2**(num_bytes * 8) - (2**(num_bytes * 8) % range_size)):
                return min_val + (rand_int % range_size)
