# dashboard/core/metrics.py
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from supabase import Client

class UserMetrics:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.log_file = "/app/logs/user_sessions.json" # Ruta dentro del contenedor Docker
        self._ensure_log_file()

    def _ensure_log_file(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def start_session(self, username: str):
        # ANTES DE INICIAR UNA NUEVA SESIÓN,
        # COMPROBAMOS SI HAY UNA SESIÓN ANTERIOR "COLGADA" SIN FINALIZAR.
        if 'session_start_time' in st.session_state and st.session_state.get('session_username') != username:
            # Si hay una sesión iniciada y el usuario es diferente,
            # cerramos la sesión del usuario anterior.
            self.end_session()

        # Ahora, procedemos a iniciar la nueva sesión si no hay una activa.
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = datetime.now()
            st.session_state.pages_visited = []
            st.session_state.session_username = username

    def track_page_visit(self, page_name: str):
        if 'pages_visited' in st.session_state:
            st.session_state.pages_visited.append(page_name)

    def end_session(self):
        if 'session_start_time' in st.session_state:
            session_end = datetime.now()
            duration = session_end - st.session_state.session_start_time
            duration_minutes = int(duration.total_seconds() / 60)
            
            session_data = {
                'username': st.session_state.get('session_username', 'unknown'),
                'session_start': st.session_state.session_start_time.isoformat(),
                'session_end': session_end.isoformat(),
                'duration_minutes': duration_minutes,
                'pages_visited': json.dumps(list(set(st.session_state.get('pages_visited', [])))) # Guardamos páginas únicas
            }
            
            try:
                self.supabase.table('user_sessions').insert(session_data).execute()
            except Exception as e:
                # Log local como respaldo si falla la inserción en Supabase
                session_data['error'] = str(e)
                self._log_to_file(session_data)
            
            # Limpiar session state
            for key in ['session_start_time', 'pages_visited', 'session_username']:
                if key in st.session_state:
                    del st.session_state[key]
    
    def _log_to_file(self, data):
        try:
            with open(self.log_file, 'r+') as f:
                logs = json.load(f)
                logs.append(data)
                f.seek(0)
                json.dump(logs, f, indent=2)
        except Exception:
            pass # Evita que un error de log crashee la app

    def get_metrics_summary(self, days=30):
        try:
            start_date = datetime.now() - timedelta(days=days)
            response = self.supabase.table('user_sessions').select("*").gte('session_start', start_date.isoformat()).execute()
            if not response.data: return None
            df = pd.DataFrame(response.data)
            df['session_start'] = pd.to_datetime(df['session_start'])
            return {
                'total_sessions': len(df),
                'unique_users': df['username'].nunique(),
                'avg_duration_minutes': df['duration_minutes'].mean(),
                'sessions_by_user': df['username'].value_counts().to_dict(),
                'sessions_by_day': df.groupby(df['session_start'].dt.date).size().to_dict()
            }
        except Exception:
            return None
    def get_recent_sessions(self, limit=50):
        """Obtiene las N sesiones más recientes de la base de datos."""
        try:
            response = self.supabase.table('user_sessions').select("*").order('session_start', desc=True).limit(limit).execute()
            if response.data:
                return pd.DataFrame(response.data)
            # Devuelve un DataFrame vacío si no hay datos o si falla
            return pd.DataFrame() 
        except Exception as e:
            # En lugar de mostrar un error que detenga la app, lo registramos y devolvemos un DF vacío
            print(f"Error al obtener sesiones recientes: {e}")
            return pd.DataFrame()


def init_metrics(supabase: Client):
    if 'metrics' not in st.session_state:
        st.session_state.metrics = UserMetrics(supabase)
    return st.session_state.metrics