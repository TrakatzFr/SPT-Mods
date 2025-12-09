import os, zipfile, shutil, sys, subprocess
from pathlib import Path


try:
    import py7zr
    SEVENZIP_AVAILABLE = True
except ImportError:
    SEVENZIP_AVAILABLE = False
    print("Note: py7zr not installed. 7z files won't be supported.")
    print("Install with: pip install py7zr")

try:
    import rarfile
    RAR_AVAILABLE = True
except ImportError:
    RAR_AVAILABLE = False
    print("Note: rarfile not installed. RAR files won't be supported.")
    print("Install with: pip install rarfile")

ZipList = None
print("Trying to init folders...")
try:
    os.mkdir("Temp")
except Exception as e:
    pass
try:
    os.chdir("Temp")
except Exception as e:
    print(e)
try:
    os.mkdir("Plugins")
except Exception as e:
    pass
try:
    os.mkdir("Mods")
except Exception as e:
    pass
try: 
    os.mkdir("Extractions")
except Exception as e:
    pass

tmpPluginPath = Path("Plugins")
tmpModPath = Path("Mods")
tmpExtPath = Path("Extractions")

def defaultDirs():
    global downloadPath, sptPath
    downloadPath = Path.home() / "Downloads"
    sptPath = Path("C:/SPT")

def main():
    defaultDirs()
    print("=" * 40)
    print("SPT AUTO MOD INSTALLER WITH 7Z & RAR SUPPORT")
    print("=" * 40)
    confirmDirs()

def confirmDirs():
    print()
    print("Current directories:")
    print(f"Archive's location (download dir)> {downloadPath}")
    print(f"Spt root path> {sptPath}")
    print("\nAre these path correct? (Y|N) (d: change back to default)")
    ui = input(">> ").lower()
    if ui == "n":
        userChangesDir()
    elif ui == "y":
        listArchives()
    elif ui == "d":
        defaultDirs()
        confirmDirs()
    else:
        print("Invalid User Input!")
        confirmDirs()

def userChangesDir():
    global downloadPath, sptPath
    print()
    downloadPath = Path(input("Path where the archive folders are> "))
    sptPath = Path(input("Root directory of your SPT installation> "))
    print("Directories changed. Please confirm...")
    print()
    confirmDirs()

def listArchives():
    global ZipList
    print("")
    print("MAKE SURE YOUR DOWNLOAD DIR ONLY HAS MOD ARCHIVES")
    print("Checking for archive files aka. mods...")
    
    # Look for all supported archive types
    archive_patterns = ["*.zip"]
    
    if SEVENZIP_AVAILABLE:
        archive_patterns.extend(["*.7z", "*.7zip"])
    
    if RAR_AVAILABLE:
        archive_patterns.extend(["*.rar", "*.cbr"])
    
    ZipList = []
    for pattern in archive_patterns:
        ZipList.extend(downloadPath.glob(pattern))
    
    print("Done!")
    print(f"Found {len(ZipList)} archives!")
    
    # Check for unsupported files if modules not available
    if not SEVENZIP_AVAILABLE:
        sevenz_files = list(downloadPath.glob("*.7z")) + list(downloadPath.glob("*.7zip"))
        if sevenz_files:
            print(f"Warning: Found {len(sevenz_files)} 7z files but py7zr not installed!")
    
    if not RAR_AVAILABLE:
        rar_files = list(downloadPath.glob("*.rar")) + list(downloadPath.glob("*.cbr"))
        if rar_files:
            print(f"Warning: Found {len(rar_files)} RAR files but rarfile not installed!")
    
    print("List the mods? (Y|N)")
    ui = input(">> ").lower()
    if ui == "n":
        installMods()
    elif ui == "y":
        for i, file in enumerate(ZipList, 1):
            print(f"{i}. {file.name}")
        installMods()
    else:
        print("Invalid User Input!")
        listArchives()

def extractZipToSPT(zip_file, spt_path):
    try:
        print(f"  Extracting {zip_file.name} to SPT root...")
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            for i, file in enumerate(file_list):
                if file.endswith('/'):
                    continue
                    
                zip_ref.extract(file, spt_path)
                
                if i % 50 == 0 and i > 0:
                    print(f"    Extracted {i}/{len(file_list)} files...")
        
        return True
    except Exception as e:
        print(f"  Error extracting {zip_file.name}: {e}")
        return False

def extract7zToSPT(sevenz_file, spt_path):
    if not SEVENZIP_AVAILABLE:
        print(f"  Error: Cannot extract {sevenz_file.name} - py7zr not installed!")
        return False
    
    try:
        print(f"  Extracting {sevenz_file.name} to SPT root...")
        
        with py7zr.SevenZipFile(sevenz_file, 'r') as archive:
            file_list = archive.getnames()
            
            archive.extractall(path=spt_path)
            
            print(f"    Extracted {len(file_list)} files...")
        
        return True
    except Exception as e:
        print(f"  Error extracting {sevenz_file.name}: {e}")
        return False

def extractRarToSPT(rar_file, spt_path):
    if not RAR_AVAILABLE:
        print(f"  Error: Cannot extract {rar_file.name} - rarfile not installed!")
        return False
    
    try:
        print(f"  Extracting {rar_file.name} to SPT root...")
        
        with rarfile.RarFile(rar_file, 'r') as archive:
            file_list = archive.namelist()
            
            archive.extractall(path=spt_path)
            
            print(f"    Extracted {len(file_list)} files...")
        
        return True
    except Exception as e:
        print(f"  Error extracting {rar_file.name}: {e}")
        return False

def backupModFiles(zip_file, spt_path):
    try:
        backup_dir = spt_path / "backups" / zip_file.stem
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        if zip_file.suffix.lower() in ['.zip']:
            with zipfile.ZipFile(zip_file, 'r') as archive:
                for file in archive.namelist():
                    if not file.endswith('/'):
                        target_file = spt_path / file
                        if target_file.exists():
                            backup_file = backup_dir / file
                            backup_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(target_file, backup_file)
        
        elif zip_file.suffix.lower() in ['.7z', '.7zip'] and SEVENZIP_AVAILABLE:
            with py7zr.SevenZipFile(zip_file, 'r') as archive:
                for file in archive.getnames():
                    if not file.endswith('/'):
                        target_file = spt_path / file
                        if target_file.exists():
                            backup_file = backup_dir / file
                            backup_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(target_file, backup_file)
        
        elif zip_file.suffix.lower() in ['.rar', '.cbr'] and RAR_AVAILABLE:
            with rarfile.RarFile(zip_file, 'r') as archive:
                for file in archive.namelist():
                    if not file.endswith('/'):
                        target_file = spt_path / file
                        if target_file.exists():
                            backup_file = backup_dir / file
                            backup_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(target_file, backup_file)
        
        return backup_dir
    except Exception as e:
        print(f"  Warning: Could not create backup: {e}")
        return None

def installMods():
    print()
    installedCount = 0
    failedCount = 0
    
    sptPath.mkdir(parents=True, exist_ok=True)
    

    print("Create backup of existing files? (Y/N)")
    backup_choice = input(">> ").lower()
    do_backup = backup_choice == 'y'
    
    for f in ZipList:
        print(f"\nInstalling: {f.name}")
        
        if do_backup:
            print(f"  Creating backup of existing files...")
            backup_dir = backupModFiles(f, sptPath)
            if backup_dir:
                print(f"  Backup created in: {backup_dir}")
        
        ext = f.suffix.lower()
        success = False
        
        if ext in ['.zip']:
            success = extractZipToSPT(f, sptPath)
        elif ext in ['.7z', '.7zip']:
            success = extract7zToSPT(f, sptPath)
        elif ext in ['.rar', '.cbr']:
            success = extractRarToSPT(f, sptPath)
        else:
            print(f"  Unsupported archive format: {ext}")
            success = False
        
        if success:
            print(f"    Successfully installed {f.name}")
            installedCount += 1
        else:
            print(f"    Failed to install {f.name}")
            failedCount += 1
    
    print(f"\n{'='*40}")
    print(f"Installation complete!")
    print(f"Successfully installed: {installedCount}")
    print(f"Failed: {failedCount}")
    
    if installedCount > 0:
        deleteChoice = input("\nDelete original archive files? (y/n): ").lower()
        if deleteChoice == 'y':
            for f in ZipList:
                try:
                    f.unlink()
                    print(f"  Deleted: {f.name}")
                except:
                    print(f"  Could not delete: {f.name}")
    
    print("\nCleaning up temp files...")
    try:
        shutil.rmtree(tmpExtPath)
        tmpExtPath.mkdir()
    except:
        pass
    
    print("\nDone! Please restart SPTarkov.")

if __name__ == "__main__":
    main()
