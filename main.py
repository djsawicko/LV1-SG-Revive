import customtkinter as ctk
import tkinter.filedialog as fd
from tkinter import messagebox
import wmi
import sqlite3
import shutil
import re
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkInterfaceManager:
    """Handles network interface detection and MAC address processing"""
    def __init__(self):
        self.wmi = wmi.WMI()
        
    def get_interfaces(self) -> List[str]:
        """Returns list of available network interfaces with MAC addresses"""
        interfaces = []
        try:
            for nic in self.wmi.Win32_NetworkAdapter():
                if nic.MACAddress:
                    interfaces.append(f"{nic.Name} ({nic.MACAddress})")
        except Exception as e:
            logger.error(f"Error getting network interfaces: {e}")
            messagebox.showerror("Error", "Could not detect network interfaces")
        return interfaces
    
    @staticmethod
    def extract_mac(interface_str: str) -> int:
        """
        Extracts MAC from string like 'Intel(R) Wireless-AC 9560 160MHz (00:00:00:00:00)'
        and converts it into LV1 friendly format
        """
        try:
            matches = re.findall(r'\(([^)]+)\)', interface_str)
            if not matches:
                raise ValueError("No MAC address found in interface string")
                
            last_value = matches[-1]  # Get last value in brackets (MAC addr)
            return int(last_value.replace(":", ""), 16)  # Convert to LV1 format
        except Exception as e:
            logger.error(f"Error processing MAC address: {e}")
            raise ValueError("Invalid MAC address format") from e


class DatabaseManager:
    """Handles all database operations for the eMotion session files"""
    @staticmethod
    def update_session(file_path: str, mac: int, bank: int, io: int) -> bool:
        """
        Updates the session file with new SG Connect device configuration
        Returns True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # Check for existing host SG Connect devices
            cursor.execute("""
                SELECT device.id 
                FROM device
                JOIN device_iobox ON device.id = device_iobox.id
                WHERE device_iobox.device_id = ? AND device_iobox.vendor_id = ?
            """, (97, 0))

            for (device_id,) in cursor.fetchall():
                cursor.execute("SELECT owner_uuid FROM device WHERE id = ?", (device_id,))
                (owner_uuid,) = cursor.fetchone()

                # Check if owner_uuid is all zeros (Session hosts)
                normalized_uuid = str(owner_uuid).replace(":", "").replace(",", "").replace(" ", "")
                if normalized_uuid.strip('0') == "":
                    if not messagebox.askokcancel(
                        "Warning", 
                        "Session already contains host Local Device. Remove it and continue?"
                    ):
                        conn.close()
                        return False

                    # Remove device and its iobox entry
                    cursor.execute("DELETE FROM device_iobox WHERE id = ? AND vendor_id = ?", (device_id, 0))
                    cursor.execute("DELETE FROM device WHERE id = ?", (device_id,))

                    
            
            # Check for device in the same slot
            cursor.execute(
                "SELECT id FROM device WHERE io_bank = ? AND assign = ?", 
                (bank, io)
            )
        
            if cursor.fetchone():
                if not messagebox.askokcancel(
                    "Warning", 
                    "Session already contains device in the selected slot. Replace it and continue?"
                ):
                    conn.close()
                    return False
                
                # Remove device and its iobox entry
                cursor.execute("DELETE FROM device_iobox WHERE id IN (SELECT id FROM device WHERE io_bank = ? AND assign = ?)", (bank, io))
                cursor.execute("DELETE FROM device WHERE id IN (SELECT id FROM device WHERE io_bank = ? AND assign = ?)", (bank, io))
                

            # Get next available ID
            cursor.execute("SELECT MAX(id) FROM device")
            result = cursor.fetchone()
            device_id = (result[0] or 0) + 1
            
            # Insert new device
            sql_script = f"""
                INSERT INTO device(
                    id, device_gender, mac, io_bank, assign, version, description,
                    in_channel_count, out_channel_count, max_in_channel_count,
                    max_out_channel_count, owner_uuid, ownership_level,
                    is_share_preamp, is_golden_box, golden_box_id
                ) VALUES(
                    {device_id}, 0, {mac}, {bank}, {io}, '1.1.1', 'SG Connect',
                    0, 0, 0, 0, '00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:', 
                    3, 0, 0, 0
                );
                INSERT INTO device_iobox(
                    id, boot_version, device_id, vendor_id, 
                    emulation_mode, midi_capable, assigned_to_midi
                ) VALUES(
                    {device_id}, '1.1.1', 97, 0, -1, 0, 0
                );
            """
            
            cursor.executescript(sql_script)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            messagebox.showerror("Error", f"Failed to update session file: {e}")
            if 'conn' in locals():
                conn.close()
            return False


class MacConfigApp(ctk.CTk):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.title("eMotion LV1 | SG Connect Revive")
        self.geometry("550x200")
        self.session: Optional[str] = None
        
        # Configure appearance
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.interface_manager = NetworkInterfaceManager()
        self.db_manager = DatabaseManager()
        self._setup_ui()
        
    def _setup_ui(self):
        """Sets up all UI components with improved layout management"""
        # Main container frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Setup section
        setup_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        setup_frame.pack(fill="x", pady=5, padx=30)
        
        # Interface selection
        iface_frame = ctk.CTkFrame(setup_frame, fg_color="transparent")
        iface_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(iface_frame, text="SG Connect network interface:").pack(anchor="c")
        self.interface_var = ctk.StringVar()
        self.interface_menu = ctk.CTkOptionMenu(
            iface_frame, 
            values=self.interface_manager.get_interfaces(),
            variable=self.interface_var,
            dynamic_resizing=False,
            anchor="c"
        )
        self.interface_menu.pack(fill="x", pady=(0, 10))
        
        # IO Slot selection
        slot_frame = ctk.CTkFrame(setup_frame, fg_color="transparent")
        slot_frame.pack(side="right")
        
        ctk.CTkLabel(slot_frame, text="IO Slot").pack()
        self.slot_var = ctk.StringVar(value="1")
        self.slot_menu = ctk.CTkOptionMenu(
            slot_frame, 
            values=[str(i) for i in range(1, 17)],
            variable=self.slot_var,
            width=80,
            anchor="c"
        )
        self.slot_menu.pack(pady=(0, 10))
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="Load Session", 
            command=self.load_file,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="Update Session", 
            command=self.save_file,
            width=120
        ).pack(side="left", padx=5)

        # Warning label
        ctk.CTkLabel(
            main_frame,
            text="⚠️ Warning: Always backup your session file before updating!",
            text_color="orange",
            font=("", 10, "bold"),
            wraplength=350  # Ensures text wraps nicely on small windows
        ).pack(pady=(0, 5))

        # Status bar
        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(
            main_frame, 
            textvariable=self.status_var,
            font=("", 10),
            fg_color=("gray85", "gray20"),
            corner_radius=5,
            height=25
        ).pack(side="bottom", fill="x", pady=(5, 0))
        
    def load_file(self):
        """Handles loading of session files"""
        file_path = fd.askopenfilename(
            filetypes=[("eMotion LV1 Session File", "*.emo")]
        )
        if file_path:
            self.session = file_path
            self.status_var.set(f"Loaded: {file_path}")
            
    def save_file(self):
        """Handles saving of session files with updated configuration"""
        if not self.session:
            messagebox.showwarning("Warning", "Please load a session file first")
            return
            
        try:
            mac = self.interface_manager.extract_mac(self.interface_var.get())
            io_slot = int(self.slot_var.get())
            
            # Calculate bank and IO position
            bank = 0 
            io = io_slot - 1
            if io >= 8: 
                bank = 1
                io = io - 8
                
            # Save a copy if needed
            save_path = fd.asksaveasfilename(
                defaultextension=".emo", 
                filetypes=[("eMotion LV1 Session File", "*.emo")],
                initialfile=self.session
            )
            
            if not save_path:
                return  # User cancelled
                
            if self.session != save_path:
                shutil.copy(self.session, save_path)
                
            # Update the database
            if self.db_manager.update_session(save_path, mac, bank, io):
                self.status_var.set(f"Successfully updated: {save_path}")
                messagebox.showinfo("Success", "Session updated successfully")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    try:
        app = MacConfigApp()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application crash: {e}")
        messagebox.showerror("Fatal Error", f"The application has crashed: {e}")
