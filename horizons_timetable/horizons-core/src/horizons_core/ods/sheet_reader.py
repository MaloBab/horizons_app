import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Optional, Any
from horizons_core.exceptions.sheet_reader_error import SheetReaderError
from horizons_core.ods.isheet_reader import ISheetReader


class SheetReader(ISheetReader):
    """
    Lecteur universel pour fichiers ODS avec gestion des cellules fusionnées.
    Traite les <table:covered-table-cell> pour maintenir les indices corrects.
    """
    
    NAMESPACES = {
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
    }
    
    def __init__(self, filepath: str, sheet_index: int = 0):
        """
        Initialise le lecteur avec diagnostic.
        
        Args:
            filepath: Chemin vers le fichier ODS
            sheet_index: Index de la feuille à lire (défaut: 0)
            
        Raises:
            SheetReaderError: Si le fichier est invalide ou la feuille introuvable
        """
        
        self._filepath = Path(filepath)
        self._sheet_index = sheet_index

        if not self._filepath.exists():
            raise SheetReaderError(f"Fichier introuvable : {filepath}")

        
        if not self._filepath.suffix.lower() == '.ods':
            raise SheetReaderError(f"Format invalide : attendu .ods, reçu {self._filepath.suffix}")
        
        try:
            self._data: list[list[Any]] = []
            self._merged_cells: dict[tuple[int, int], dict[str, int]] = {}
            self._row_count: int = 0
            self._column_count: int = 0
            self._load_ods()
            
        except Exception as e:
            raise SheetReaderError(f"Erreur lors du chargement du fichier : {e}") from e
    
    def _load_ods(self) -> None:
        """Charge les données depuis un fichier ODS en parsant le XML."""
        try:
            with zipfile.ZipFile(self._filepath, 'r') as ods_file:
                xml_info = ods_file.getinfo('content.xml')
                xml_size_mb = xml_info.file_size / (1024 * 1024)
                
                
                if xml_size_mb > 100:
                    raise SheetReaderError(
                        f"⚠️  content.xml trop volumineux ({xml_size_mb:.2f} MB)\n"
                        f"      Le fichier contient probablement des milliers de lignes vides.\n"
                        f"      Solution: nettoyez le fichier dans LibreOffice."
                    )
                
                with ods_file.open('content.xml') as content:
                    tree = ET.parse(content)
                    root = tree.getroot()
                    tables = root.findall('.//table:table', self.NAMESPACES)
                    
                    if self._sheet_index >= len(tables):
                        raise SheetReaderError(
                            f"Index de feuille {self._sheet_index} hors limites "
                            f"(nombre de feuilles : {len(tables)})"
                        )
                    table = tables[self._sheet_index]
                    self._parse_table(table)
                    
                    self._row_count = len(self._data)
                    self._column_count = max(len(row) for row in self._data) if self._data else 0
                    
                    
        except zipfile.BadZipFile as e:
            raise SheetReaderError(f"Fichier ODS corrompu : {e}") from e
        except ET.ParseError as e:
            raise SheetReaderError(f"XML invalide dans le fichier ODS : {e}") from e
    
    def _parse_table(self, table: ET.Element) -> None:
        """
        Parse une table XML et extrait les données et fusions.
        """
        row_index = 0
        
        all_rows = table.findall('table:table-row', self.NAMESPACES)
        
        for row_elem in all_rows:
            num_rows_repeated = int(
                row_elem.attrib.get(
                    f'{{{self.NAMESPACES["table"]}}}number-rows-repeated',
                    1
                )
            )
            
            if num_rows_repeated > 2000:
                num_rows_repeated = min(num_rows_repeated, 100)
            
            row_data = self._parse_row(row_elem, row_index)
            
            for _ in range(num_rows_repeated):
                self._data.append(row_data.copy())
                row_index += 1
            
            if row_index > 50000:
                break
    
    def _parse_row(self, row_elem: ET.Element, row_index: int) -> list[Any]:
        """
        Parse une ligne XML et extrait les valeurs des cellules.
        
        Args:
            row_elem: Élément XML de la ligne
            row_index: Index de la ligne actuelle
            
        Returns:
            Liste des valeurs de la ligne
        """
        row_data = []
        col_index = 0
        
        for cell in row_elem:
            tag_name = cell.tag.split('}')[-1] if '}' in cell.tag else cell.tag

            if tag_name == 'table-cell':
                cols_spanned = int(
                    cell.attrib.get(
                        f'{{{self.NAMESPACES["table"]}}}number-columns-spanned',
                        1
                    )
                )
                rows_spanned = int(
                    cell.attrib.get(
                        f'{{{self.NAMESPACES["table"]}}}number-rows-spanned',
                        1
                    )
                )
                
                num_cols_repeated = int(
                    cell.attrib.get(
                        f'{{{self.NAMESPACES["table"]}}}number-columns-repeated',
                        1
                    )
                )
                
                if num_cols_repeated > 1000:
                    num_cols_repeated = min(num_cols_repeated, 100)
                

                value = self._extract_cell_value(cell)
                
                if cols_spanned > 1 or rows_spanned > 1:
                    self._merged_cells[(row_index, col_index)] = {
                        'colspan': cols_spanned,
                        'rowspan': rows_spanned
                    }
 
                for _ in range(num_cols_repeated):
                    row_data.append(value)
                    col_index += 1
            
            elif tag_name == 'covered-table-cell':
                num_cols_repeated = int(
                    cell.attrib.get(
                        f'{{{self.NAMESPACES["table"]}}}number-columns-repeated',
                        1
                    )
                )
                
                if num_cols_repeated > 1000:
                    num_cols_repeated = min(num_cols_repeated, 100)
                
                for _ in range(num_cols_repeated):
                    row_data.append(None)
                    col_index += 1
        
        return row_data
    
    def _extract_cell_value(self, cell: ET.Element) -> Optional[str]:
        """
        Extrait la valeur textuelle d'une cellule XML.
        
        Args:
            cell: Élément XML de la cellule
            
        Returns:
            Valeur de la cellule ou None
        """
        text_elements = cell.findall('.//text:p', self.NAMESPACES)
        
        if not text_elements:
            return None
        
        texts = []
        for p in text_elements:
            if p.text:
                texts.append(p.text)
            for child in p:
                if child.text:
                    texts.append(child.text)
                if child.tail:
                    texts.append(child.tail)
        
        combined = ' '.join(texts).strip()
        return combined if combined else None
    
    def get_value(self, row: int, col: int) -> Optional[str]:
        """
        Récupère la valeur d'une cellule.
        
        Args:
            row: Numéro de ligne (0-indexed)
            col: Numéro de colonne (0-indexed)
            
        Returns:
            Valeur de la cellule (nettoyée) ou None
        """
        if row < 0 or col < 0:
            raise IndexError(f"Indices négatifs invalides : row={row}, col={col}")
        
        if row >= self._row_count:
            return None
        
        if col >= len(self._data[row]):
            return None
        
        value = self._data[row][col]
        
        if value is None:
            return None
        
        str_value = str(value).strip()
        return str_value if str_value else None
    
    def get_row_count(self) -> int:
        """Retourne le nombre total de lignes (cached)."""
        return self._row_count
    
    def get_column_count(self) -> int:
        """Retourne le nombre maximum de colonnes (cached)."""
        return self._column_count
    
    def get_merge_info(self, row: int, col: int) -> Optional[dict[str, int]]:
        """Récupère les informations de fusion d'une cellule."""
        return self._merged_cells.get((row, col))
    
    def get_row(self, row: int) -> list[Optional[str]]:
        """Récupère toutes les valeurs d'une ligne."""
        if row < 0 or row >= self._row_count:
            raise IndexError(f"Index de ligne invalide : {row}")
        
        return [self.get_value(row, col) for col in range(self._column_count)]
    
    def get_column(self, col: int) -> list[Optional[str]]:
        """Récupère toutes les valeurs d'une colonne."""
        if col < 0 or col >= self._column_count:
            raise IndexError(f"Index de colonne invalide : {col}")
        
        return [self.get_value(row, col) for row in range(self._row_count)]