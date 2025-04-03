import secrets
import base64
import os
import argparse
from dotenv import load_dotenv, find_dotenv

def generate_key(length=32):
    """
    Generate a secure random key with the specified byte length
    
    Args:
        length (int): Length of the key in bytes
        
    Returns:
        str: Base64 encoded random key
    """
    # Generate random bytes
    random_bytes = secrets.token_bytes(length)
    
    # Convert to base64 for a string representation
    encoded_key = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    
    return encoded_key

def update_env_file(key, env_file='.env'):
    """
    Update the JWT_SECRET_KEY in the .env file
    
    Args:
        key (str): The new secret key
        env_file (str): Path to the .env file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Make sure .env file exists
    if not os.path.exists(env_file):
        print(f"Error: {env_file} file not found.")
        return False
    
    # Read the current contents
    with open(env_file, 'r') as file:
        lines = file.readlines()
    
    # Find and replace the JWT_SECRET_KEY line, or add it if not found
    jwt_key_found = False
    for i, line in enumerate(lines):
        if line.strip().startswith('JWT_SECRET_KEY='):
            lines[i] = f'JWT_SECRET_KEY={key}\n'
            jwt_key_found = True
            break
    
    if not jwt_key_found:
        lines.append(f'JWT_SECRET_KEY={key}\n')
    
    # Write back to the file
    with open(env_file, 'w') as file:
        file.writelines(lines)
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Generate a secure JWT secret key')
    parser.add_argument('--length', type=int, default=32, help='Length of the key in bytes (default: 32)')
    parser.add_argument('--update-env', action='store_true', help='Update the .env file with the new key')
    parser.add_argument('--env-file', default='.env', help='Path to the .env file (default: .env)')
    
    args = parser.parse_args()
    
    # Generate key
    key = generate_key(args.length)
    
    print(f"Generated JWT Secret Key: {key}")
    print("\nThis key is cryptographically secure and suitable for use in production.")
    
    # Update .env file if requested
    if args.update_env:
        if update_env_file(key, args.env_file):
            print(f"\nSuccessfully updated JWT_SECRET_KEY in {args.env_file}")
        else:
            print(f"\nFailed to update {args.env_file}")
            print("You can manually add the key to your .env file:")
            print(f"JWT_SECRET_KEY={key}")
    else:
        print("\nTo use this key, add it to your .env file:")
        print(f"JWT_SECRET_KEY={key}")

if __name__ == "__main__":
    main() 