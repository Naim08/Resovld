from interfaces.database import DatabaseI
from supabase import create_client


class Supabase(DatabaseI):

    def __init__(self, api_key, url):
        self.supabase = create_client(url, api_key)
    
    def fetch_repo_info_with_alert_service_id(self, table_name, column_name, alert_service_id):
        return self.supabase.table(table_name).select('*').eq(column_name, alert_service_id).execute()