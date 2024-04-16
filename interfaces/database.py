from abc import ABC, abstractmethod


class DatabaseI(ABC):
    
    def fetch_repo_info_with_alert_service_id(self, table_name, column_name, alert_service_id):
        pass