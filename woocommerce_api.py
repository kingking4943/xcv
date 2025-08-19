#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo WooCommerce API per Gestionale Gitemania (Versione Finale con Paginazione e Callback Real-time)
"""
import threading, time, requests # Importa 'requests'
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Callable
from woocommerce import API
from config import config

class WooCommerceManager:
    def __init__(self, on_order_update: Callable = None):
        self.api = None
        self.sync_running = False
        self.on_order_update = on_order_update or (lambda orders: None)
        self.last_sync = datetime.now(timezone.utc) - timedelta(days=1)
        
    def initialize(self, base_url: str, consumer_key: str, consumer_secret: str) -> bool:
        try:
            self.api = API(url=base_url, consumer_key=consumer_key, consumer_secret=consumer_secret,
                           version="wc/v3", timeout=60, verify_ssl=True)
            response = self.api.get("system_status")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Errore inizializzazione WooCommerce: {e}")
            return False
            
    def start_sync(self):
        if self.sync_running: return
        self.sync_running = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        print("🔄 Sincronizzazione periodica avviata")
        
    def stop_sync(self):
        self.sync_running = False
        print("⏹️ Sincronizzazione periodica fermata")
        
    def _polling_loop(self):
        while self.sync_running:
            try:
                updated_orders = self.fetch_orders_since(self.last_sync)
                if updated_orders:
                    self.on_order_update(updated_orders)
                    self.last_sync = datetime.now(timezone.utc)
                time.sleep(config.get('app', 'sync_interval', 60))
            except Exception as e:
                print(f"❌ Errore polling: {e}")
                time.sleep(60)

    def fetch_orders_since(self, since_datetime: datetime) -> Optional[List[Dict]]:
        if not self.api: return None
        try:
            params = {"after": since_datetime.isoformat()}
            response = self.api.get("orders", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Errore durante il recupero degli ordini da {since_datetime}: {e}")
            return None

    def fetch_last_day_orders(self) -> Optional[List[Dict]]:
        if not self.api: return None
        try:
            twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(days=1)
            return self.fetch_orders_since(twenty_four_hours_ago)
        except Exception as e:
            print(f"❌ Errore durante il recupero degli ordini delle ultime 24 ore: {e}")
            return None

    def get_orders_paged(self, params: dict = None, page_callback: Callable = None) -> bool:
        if not self.api: return False
        page = 1
        per_page = 100
        try:
            while True:
                current_params = {'per_page': per_page, 'page': page}
                if params: current_params.update(params)
                print(f"📄 Download pagina {page} di ordini...")
                response = self.api.get('orders', params=current_params)
                response.raise_for_status()
                orders_page = response.json()
                if not orders_page:
                    print("✅ Download di tutte le pagine completato.")
                    break
                if page_callback:
                    page_callback(orders_page)
                if len(orders_page) < per_page:
                    print("✅ Raggiunta l'ultima pagina.")
                    break
                page += 1
                time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Eccezione grave in get_orders_paged (pagina {page}): {e}")
            return False

    def get_viaggiatori_for_order(self, order_id: int) -> Optional[List[Dict]]:
        """
        Chiama l'endpoint API custom per ottenere i dati dei viaggiatori.
        USA 'requests' DIRETTAMENTE PER EVITARE IL NAMESPACE wc/v3.
        """
        if not self.api:
            return None
        try:
            # Costruisce l'URL corretto manualmente
            url = f"{self.api.url}/wp-json/gitemania/v1/viaggiatori/{order_id}"
            
            # Esegue la richiesta con l'autenticazione corretta
            response = requests.get(
                url,
                auth=(self.api.consumer_key, self.api.consumer_secret),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Errore nel recuperare i dati viaggiatori per l'ordine {order_id}: {e}")
            return None
