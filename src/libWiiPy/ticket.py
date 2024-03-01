# "ticket.py" from libWiiPy by NinjaCheetah & Contributors
# https://github.com/NinjaCheetah/libWiiPy
#
# See https://wiibrew.org/wiki/Ticket for details about the TMD format

import io
from .crypto import decrypt_title_key
from dataclasses import dataclass
from typing import List


@dataclass
class TitleLimit:
    """Creates a TitleLimit object that contains the type of restriction and the limit."""
    # The type of play limit applied. The following types exist:
    # 0 = None, 1 = Time Limit, 3 = None, 4 = Launch Count
    limit_type: int
    # The maximum value of the limit applied.
    # This is either the number of minutes for a time limit, or the number of launches for a launch limit.
    maximum_usage: int


class Ticket:
    """Creates a Ticket object to parse a Ticket file to retrieve the Title Key needed to decrypt it."""

    def __init__(self, ticket):
        self.ticket = ticket
        # Signature blob header
        self.signature_type: bytes  # Type of signature, always 0x10001 for RSA-2048
        self.signature: bytes  # Actual signature data
        # v0 ticket data
        self.signature_issuer: str  # Who issued the signature for the ticket
        self.ecdh_data: bytes  # Involved in created one-time keys for console-specific title installs.
        self.ticket_version: int  # The version of the ticket format.
        self.title_key_enc: bytes  # The title key of the ticket's respective title, encrypted by a common key.
        self.ticket_id: bytes  # Used as the IV when decrypting the title key for console-specific title installs.
        self.console_id: int  # ID of the console that the ticket was issued for.
        self.title_id: bytes  # TID/IV used for AES-CBC encryption.
        self.title_version: int  # Version of the ticket's associated title.
        self.permitted_titles: bytes  # Permitted titles mask
        self.permit_mask: bytes  # "Permit mask. The current disc title is ANDed with the inverse of this mask to see if the result matches the Permitted Titles Mask."
        self.title_export_allowed: int  # Whether title export is allowed with a PRNG key or not.
        self.common_key_index: int  # Which common key should be used. 0 = Common Key, 1 = Korean Key, 2 = vWii Key
        self.content_access_permissions: bytes  # "Content access permissions (one bit for each content)"
        self.title_limits_list: List[TitleLimit] = []  # List of play limits applied to the title.
        # v1 ticket data
        # TODO: Figure out v1 ticket stuff
        with io.BytesIO(self.ticket) as ticketdata:
            # ====================================================================================
            # Parses each of the keys contained in the Ticket.
            # ====================================================================================
            # Signature type
            ticketdata.seek(0x0)
            self.signature_type = ticketdata.read(4)
            # Signature data
            ticketdata.seek(0x04)
            self.signature = ticketdata.read(256)
            # Signature issuer
            ticketdata.seek(0x140)
            self.signature_issuer = str(ticketdata.read(64).decode())
            # ECDH data
            ticketdata.seek(0x180)
            self.ecdh_data = ticketdata.read(60)
            # Ticket version
            ticketdata.seek(0x1BC)
            self.ticket_version = int.from_bytes(ticketdata.read(1))
            # Title Key (Encrypted by a common key)
            ticketdata.seek(0x1BF)
            self.title_key_enc = ticketdata.read(16)
            # Ticket ID
            ticketdata.seek(0x1D0)
            self.ticket_id = ticketdata.read(8)
            # Console ID
            ticketdata.seek(0x1D8)
            self.console_id = int.from_bytes(ticketdata.read(4))
            # Title ID
            ticketdata.seek(0x1DC)
            self.title_id = ticketdata.read(8)
            # Title version
            ticketdata.seek(0x1E6)
            title_version_high = int.from_bytes(ticketdata.read(1)) * 256
            ticketdata.seek(0x1E7)
            title_version_low = int.from_bytes(ticketdata.read(1))
            self.title_version = title_version_high + title_version_low
            # Permitted titles mask
            ticketdata.seek(0x1E8)
            self.permitted_titles = ticketdata.read(4)
            # Permit mask
            ticketdata.seek(0x1EC)
            self.permit_mask = ticketdata.read(4)
            # Whether title export with a PRNG key is allowed
            ticketdata.seek(0x1F0)
            self.title_export_allowed = int.from_bytes(ticketdata.read(1))
            # Common key index
            ticketdata.seek(0x1F1)
            self.common_key_index = int.from_bytes(ticketdata.read(1))
            # Content access permissions
            ticketdata.seek(0x222)
            self.content_access_permissions = ticketdata.read(64)
            # Content limits
            ticketdata.seek(0x264)
            for limit in range(0, 8):
                limit_type = int.from_bytes(ticketdata.read(4))
                limit_value = int.from_bytes(ticketdata.read(4))
                self.title_limits_list.append(TitleLimit(limit_type, limit_value))

    def get_signature(self):
        """Returns the signature of the ticket."""
        return self.signature

    def get_ticket_version(self):
        """Returns the version of the ticket."""
        return self.ticket_version

    def get_title_key_enc(self):
        """Returns the title key contained in the ticket, in encrypted form."""
        return self.title_key_enc

    def get_ticket_id(self):
        """Returns the ID of the ticket."""
        return self.ticket_id

    def get_console_id(self):
        """Returns the ID of the console this ticket is designed for, if the ticket is console-specific."""
        return self.console_id

    def get_title_id(self):
        """Returns the Title ID of the ticket's associated title."""
        title_id_str = str(self.title_id.decode())
        return title_id_str

    def get_title_version(self):
        """Returns the version of the ticket's associated title that this ticket is designed for."""
        return self.title_version

    def get_common_key_index(self):
        """Returns the index of the common key used to encrypt the Title Key contained in the ticket."""
        return self.common_key_index

    def get_common_key_type(self):
        """Returns the name of the common key used to encrypt the Title Key contained in the ticket."""
        match self.common_key_index:
            case 0:
                return "Common"
            case 1:
                return "Korean"
            case 2:
                return "vWii"

    def get_title_key(self):
        """Returns the decrypted title key contained in the ticket."""
        title_key = decrypt_title_key(self.title_key_enc, self.common_key_index, self.title_id)
        return title_key

