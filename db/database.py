"""
Veritabanı bağlantı ve işlemleri
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class Database:
    """SQLite Veritabanı Yöneticisi"""
    
    def __init__(self):
        self.db_path = settings.database_path
    
    @contextmanager
    def get_connection(self):
        """Bağlantı context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    # ==================== ÜRÜN İŞLEMLERİ ====================
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Barkod ile ürün sorgula"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM products WHERE barcode = ?
            """, (barcode,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Ürün adı veya marka ile ara"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_term = f"%{query}%"
            cursor.execute("""
            SELECT * FROM products 
            WHERE product_name LIKE ? OR brand LIKE ?
            LIMIT ?
            """, (search_term, search_term, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def create_product(self, product_data: Dict[str, Any]) -> int:
        """Yeni ürün oluştur"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO products
            (barcode, product_name, brand, risk_level, contains_gluten,
             contains_cross_contamination, certified_gluten_free, 
             ingredients_text, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data.get("barcode"),
                product_data.get("product_name"),
                product_data.get("brand"),
                product_data.get("risk_level"),
                product_data.get("contains_gluten"),
                product_data.get("contains_cross_contamination", False),
                product_data.get("certified_gluten_free", False),
                product_data.get("ingredients_text"),
                product_data.get("source")
            ))
            return cursor.lastrowid
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Ürün güncelle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Güncellenecek alanları belirle
            updates = []
            params = []
            for key, value in product_data.items():
                if value is not None and key != "id":
                    updates.append(f"{key} = ?")
                    params.append(value)
            
            if not updates:
                return False
            
            params.append(product_id)
            
            query = f"""
            UPDATE products SET {', '.join(updates)}, updated_date = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_product(self, product_id: int) -> bool:
        """Ürün sil"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return cursor.rowcount > 0
    
    # ==================== GLUTEN TEMİZLEYİCİLERİ ====================
    
    def get_flagged_ingredients(self) -> List[Dict[str, Any]]:
        """Tüm gluten tetikleyicilerini getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM flagged_ingredients")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_dangerous_ingredients(self) -> List[str]:
        """Tehlikeli malzemeleri getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT ingredient FROM flagged_ingredients 
            WHERE risk_level = 'dangerous'
            """)
            return [row[0] for row in cursor.fetchall()]
    
    def get_risky_keywords(self) -> List[str]:
        """Riskli kelimeleri getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT ingredient FROM flagged_ingredients 
            WHERE risk_level = 'risky'
            """)
            return [row[0] for row in cursor.fetchall()]
    
    # ==================== İSTATİSTİKLER ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Veritabanı istatistiklerini getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE risk_level = 'safe'")
            safe_products = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE risk_level = 'dangerous'")
            dangerous_products = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM flagged_ingredients")
            total_ingredients = cursor.fetchone()[0]
            
            return {
                "total_products": total_products,
                "safe_products": safe_products,
                "dangerous_products": dangerous_products,
                "total_flagged_ingredients": total_ingredients
            }


# Global database instance
db = Database()
