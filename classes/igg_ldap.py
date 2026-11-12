
from ldap3 import Server, Connection, SUBTREE, NONE
from ldap3.core.exceptions import LDAPBindError, LDAPException
from ldap3.utils.conv import escape_filter_chars
from urllib.parse import urlparse

class IGGldap:
    st = None


    #-----------------------------------GENERALI
    def __init__(self, st):
        self.st = st

    def login(self, username, password):
        conn = None

        try:
            ldap_host = self.st.secrets["ldap_host"]
            ldap_dn = self.st.secrets["ldap_dn"]
            ldap_domain = self.st.secrets["ldap_domain"]

            parsed = urlparse(ldap_host)
            server = Server(
                parsed.hostname or ldap_host,
                port=parsed.port,
                use_ssl=(parsed.scheme == "ldaps"),
                get_info=NONE
            )

            conn = Connection(
                server,
                user=username + ldap_domain,
                password=password,
                auto_bind=True,
                auto_referrals=False
            )

            search_filter = f"(sAMAccountName={escape_filter_chars(username)})"
            result = conn.search(
                search_base=ldap_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=["description", "mail"]
            )
            if not result:
                self.st.error("La ricerca su LDAP è fallita.")
                return None

            if not conn.entries:
                self.st.error("Utente non trovato su LDAP.")
                return None

            entry = conn.entries[0]
            national_code = entry.description.value or ""
            email = entry.mail.value or ""
            fullname = entry.entry_dn.split(",")[0].split("=", 1)[1]

            # Restituzione dati utente
            return {
                "fullname": fullname,
                "email": email,
                "national_code": national_code,
                "username": username
            }

        except LDAPBindError:
            self.st.error("Autenticazione LDAP fallita: username o password non validi.")
            return None

        except LDAPException as e:
            self.st.error(f"Errore LDAP: {e}")
            return None

        except Exception as e:
            self.st.error(f"Errore durante il login: {e}")
            return None

        finally:
            if conn:
                conn.unbind()

