from ftplib import FTP
import uuid

def list_ftp_folder(host, username, password, remote_folder):
    try:
        # Connect to the FTP server
        ftp = FTP(host)
        ftp.login(user=username, passwd=password)
        
        print(f"Connected to FTP server: {host}")
        
        # Navigate to the specified folder
        ftp.cwd(remote_folder)
        
        # List the contents of the folder
        files_and_dirs = ftp.nlst()
        
        print(f"Contents of '{remote_folder}':")
        for item in files_and_dirs:
            print(f"- {item}")
        
        return files_and_dirs
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        if 'ftp' in locals():
            ftp.quit()



# list_ftp_folder(ftp_host, ftp_user, ftp_password, ftp_directory)

def upload_photo_to_ftp(local_file_path, remote_folder):
    host = "hotelexplorer.net"
    username = "test@hotelexplorer.net"
    password = "A6s-i^jvn9-tUtBQ"
    try:
        # Connect to the FTP server
        ftp = FTP(host)
        ftp.login(user=username, passwd=password)
        
        print(f"Connected to FTP server: {host}")
        
        # Navigate to the target folder
        ftp.cwd(remote_folder)
        
        # Get the file name from the local file path
        file_name = local_file_path.split('/')[-1]

        # Generate a unique file name with .webp extension
        # unique_id = uuid.uuid4().hex  # Generate a unique identifier
        # file_extension = local_file_path.split('.')[-1]
        # unique_file_name = f"{unique_id}.{file_extension}"
        
        # # Open the local file in binary mode
        # with open(local_file_path, 'rb') as file:
        #     # Upload the file with the unique name
        #     ftp.storbinary(f"STOR {unique_file_name}", file)
            
        
        # Open the local file in binary mode
        with open(local_file_path, 'rb') as file:
            # Upload the file
            ftp.storbinary(f"STOR {file_name}", file)
        
        print(f"Photo '{file_name}' uploaded successfully to '{remote_folder}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'ftp' in locals():
            ftp.quit()

# Example usage
# Example usage
ftp_host = "hotelexplorer.net"
ftp_user = "test@hotelexplorer.net"
ftp_password = "A6s-i^jvn9-tUtBQ"
remote_folder = "/public_html/storage/upload/"
local_photo = ""

# upload_photo_to_ftp(local_photo, remote_folder)


