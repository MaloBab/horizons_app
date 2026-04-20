import logging
from typing import Any
from collections import defaultdict
from datetime import datetime

from horizons_genetic.genetic.core.chromosome import Chromosome

try:
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.style import (
        Style, TextProperties, ParagraphProperties,
        TableCellProperties, TableColumnProperties
    )
    from odf.text import P
    from odf.table import Table, TableRow, TableCell, TableColumn
except ImportError as e:
    raise ImportError("Le module odfpy est requis: pip install odfpy") from e

logger = logging.getLogger(__name__)


class ODSExporter:
    """Exporteur ODS avec design professionnel et ergonomique."""

    COLORS = {
        'header':           '#2C3E50',
        'header_text':      '#FFFFFF',
        'subheader':        '#34495E',
        'alt_row':          '#ECF0F1',
        'highlight':        '#3498DB',
        'success':          '#27AE60',
        'warning':          '#F39C12',
        'danger':           '#E74C3C',
        'info':             '#9B59B6',
        'border':           '#BDC3C7',
        'cat_bar':          '#E67E22',
        'cat_resto':        '#E74C3C',
        'cat_catering':     '#F39C12',
        'cat_securite':     '#C0392B',
        'cat_prevention':   '#8E44AD',
        'cat_ticketterie':  '#2980B9',
        'cat_camping':      '#16A085',
        'cat_billetterie':  '#27AE60',
        'cat_animations':   '#F1C40F',
        'cat_accueil':      '#3498DB',
        'cat_acces':        '#95A5A6',
        'cat_environnement':'#1ABC9C',
        'cat_logistique':   '#7F8C8D',
        'cat_technique':    '#34495E',
    }

    def __init__(self) -> None:
        self.doc: Any = OpenDocumentSpreadsheet()
        self.styles: dict[str, Any] = {}
        self.column_styles: dict[str, Any] = {}

    def export(self, chromosome: Chromosome, filepath: str) -> None:
        self.doc = OpenDocumentSpreadsheet()
        self._create_styles()
        self._create_column_styles()

        self._create_statistics_sheet(chromosome)
        self._create_benevole_view(chromosome)
        self._create_poste_view(chromosome)
        self._create_calendar_view(chromosome)
        self._create_legend_sheet()

        self.doc.save(filepath)
        logger.info(f"✅ Export terminé: {filepath}")

    # ========================================================================
    # STYLES
    # ========================================================================

    def _create_column_styles(self) -> None:
        """Crée les styles de colonnes avec largeurs personnalisées."""
        specs = {
            'narrow':      '2.8cm',
            'medium':      '4.2cm',
            'wide':        '6.4cm',
            'extra_wide':  '8.5cm',
        }
        for name, width in specs.items():
            style = Style(name=f"{name.capitalize()}Column", family="table-column")
            style.addElement(TableColumnProperties(columnwidth=width))
            self.doc.automaticstyles.addElement(style)
            self.column_styles[name] = style

    def _create_styles(self) -> None:
        """Crée tous les styles de cellules du document."""
        self._add_cell_style(
            'header',
            bg=self.COLORS['header'],
            text_color=self.COLORS['header_text'],
            bold=True, fontsize="12pt", align="center",
            border=f"0.05cm solid {self.COLORS['border']}", padding="0.1cm"
        )
        self._add_cell_style(
            'subheader',
            bg=self.COLORS['subheader'],
            text_color=self.COLORS['header_text'],
            bold=True, fontsize="10pt", align="center",
            border=f"0.05cm solid {self.COLORS['border']}", padding="0.08cm"
        )
        self._add_cell_style(
            'alt_row',
            bg=self.COLORS['alt_row'],
            fontsize="10pt",
            border=f"0.02cm solid {self.COLORS['border']}", padding="0.05cm"
        )
        self._add_cell_style(
            'normal',
            fontsize="10pt",
            border=f"0.02cm solid {self.COLORS['border']}", padding="0.05cm"
        )
        for key in ('highlight', 'success', 'warning', 'danger', 'info'):
            self._add_cell_style(
                key,
                bg=self.COLORS[key],
                text_color=self.COLORS['header_text'],
                bold=True,
                border=f"0.02cm solid {self.COLORS['border']}", padding="0.05cm"
            )
        for cat_key, color in self.COLORS.items():
            if cat_key.startswith('cat_'):
                self._add_cell_style(
                    cat_key,
                    bg=color,
                    text_color=self.COLORS['header_text'],
                    fontsize="9pt",
                    border=f"0.02cm solid {self.COLORS['border']}", padding="0.05cm"
                )

    def _add_cell_style(
        self,
        name: str,
        bg: str = "",
        text_color: str = "",
        bold: bool = False,
        fontsize: str = "10pt",
        align: str = "",
        border: str = "",
        padding: str = "0.05cm"
    ) -> None:
        style = Style(name=f"{name}_style", family="table-cell")

        cell_props: dict[str, str] = {"padding": padding}
        if bg:
            cell_props["backgroundcolor"] = bg
        if border:
            cell_props["border"] = border
        style.addElement(TableCellProperties(**cell_props))

        text_props: dict[str, str] = {"fontsize": fontsize}
        if text_color:
            text_props["color"] = text_color
        if bold:
            text_props["fontweight"] = "bold"
        style.addElement(TextProperties(**text_props))

        if align:
            style.addElement(ParagraphProperties(textalign=align))

        self.doc.styles.addElement(style)
        self.styles[name] = style

    # ========================================================================
    # FEUILLES
    # ========================================================================

    def _create_statistics_sheet(self, chromosome: Chromosome) -> None:
        table = Table(name="📊 Statistiques")
        table.addElement(TableColumn(stylename=self.column_styles['wide']))
        table.addElement(TableColumn(stylename=self.column_styles['medium']))
        table.addElement(TableColumn(stylename=self.column_styles['medium']))
        table.addElement(TableColumn(stylename=self.column_styles['medium']))

        title_row = TableRow()
        title_cell = TableCell(stylename=self.styles['header'], numbercolumnsspanned=4)
        title_cell.addElement(P(text=f"📊 STATISTIQUES - {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
        title_row.addElement(title_cell)
        for _ in range(3):
            title_row.addElement(TableCell())
        table.addElement(title_row)
        table.addElement(TableRow())

        assigned = chromosome.get_assigned_benevoles()
        filled   = chromosome.count_filled_positions()
        total    = chromosome.count_total_positions()
        benevole_hours = self._compute_benevole_hours(chromosome)
        overloaded = [b for b, hours in benevole_hours.items() if any(h > 6 for h in hours)]

        stats_data = [
            ("Bénévoles affectés",  len(assigned),                             "success"),
            ("Positions remplies",  filled,                                    "success"),
            ("Positions totales",   total,                                     "info"),
            ("Taux de remplissage", f"{filled/total*100:.1f}%" if total else "N/A", "highlight"),
            ("Bénévoles surchargés",len(overloaded), "warning" if overloaded else "success"),
        ]

        for label, value, style_key in stats_data:
            row = TableRow()
            lbl = TableCell(stylename=self.styles['subheader'])
            lbl.addElement(P(text=label))
            row.addElement(lbl)
            val = TableCell(stylename=self.styles.get(style_key, self.styles['normal']))
            val.addElement(P(text=str(value)))
            row.addElement(val)
            row.addElement(TableCell())
            row.addElement(TableCell())
            table.addElement(row)

        self.doc.spreadsheet.addElement(table)

    def _create_benevole_view(self, chromosome: Chromosome) -> None:
        table = Table(name="👥 Planning par Bénévole")
        for col_key in ('wide', 'extra_wide', 'extra_wide', 'extra_wide', 'narrow'):
            table.addElement(TableColumn(stylename=self.column_styles[col_key]))

        header_row = TableRow()
        for h in ["Bénévole", "Vendredi", "Samedi", "Dimanche", "Total heures"]:
            cell = TableCell(stylename=self.styles['header'])
            cell.addElement(P(text=h))
            header_row.addElement(cell)
        table.addElement(header_row)

        benevole_data = self._organize_by_benevole(chromosome)

        for idx, (benevole_name, assignments) in enumerate(sorted(benevole_data.items())):
            row   = TableRow()
            style = self.styles['alt_row'] if idx % 2 == 0 else self.styles['normal']

            name_cell = TableCell(stylename=self.styles['subheader'])
            name_cell.addElement(P(text=benevole_name))
            row.addElement(name_cell)

            jours_data  = self._group_by_day(assignments)
            total_hours = 0

            for jour_idx in [4, 5, 6]:
                jour_assignments = jours_data.get(jour_idx, [])
                if jour_assignments:
                    hours = sum(
                        p.get_horaire().get_borne_sup() - p.get_horaire().get_borne_inf()
                        for p in jour_assignments
                    )
                    total_hours += hours
                    text = "\n".join(
                        f"• {p._categorie} ({p.get_horaire()})" for p in jour_assignments
                    )
                    cell = TableCell(stylename=self.styles.get('warning', style) if hours > 6 else style)
                    cell.addElement(P(text=text))
                else:
                    cell = TableCell(stylename=style)
                    cell.addElement(P(text="-"))
                row.addElement(cell)

            total_cell = TableCell(stylename=self.styles['highlight'])
            total_cell.addElement(P(text=f"{total_hours}h"))
            row.addElement(total_cell)
            table.addElement(row)

        self.doc.spreadsheet.addElement(table)

    def _create_poste_view(self, chromosome: Chromosome) -> None:
        table = Table(name="📋 Affectation par Poste")
        for col_key in ('medium', 'wide', 'medium', 'extra_wide', 'narrow'):
            table.addElement(TableColumn(stylename=self.column_styles[col_key]))

        header_row = TableRow()
        for h in ["Catégorie", "Poste", "Horaire", "Bénévoles affectés", "Capacité"]:
            cell = TableCell(stylename=self.styles['header'])
            cell.addElement(P(text=h))
            header_row.addElement(cell)
        table.addElement(header_row)

        postes_sorted = sorted(
            chromosome.affectations.keys(),
            key=lambda p: (p.get_categorie().pole_id, p.get_horaire().get_jour(), p.get_horaire().get_borne_inf())
        )

        current_category = None
        for idx, poste in enumerate(postes_sorted):
            benevoles = chromosome.affectations[poste]

            if current_category != poste._categorie:
                current_category = poste._categorie
                sep_row  = TableRow()
                sep_cell = TableCell(stylename=self.styles['subheader'], numbercolumnsspanned=5)
                sep_cell.addElement(P(text=f"🏷️ {current_category.nom.upper()}"))
                sep_row.addElement(sep_cell)
                for _ in range(4):
                    sep_row.addElement(TableCell())
                table.addElement(sep_row)

            row   = TableRow()
            style = self.styles['alt_row'] if idx % 2 == 0 else self.styles['normal']

            cat_key  = self._get_category_style_key(poste.get_categorie().pole_id)
            cat_cell = TableCell(stylename=self.styles.get(cat_key, style))
            cat_cell.addElement(P(text=poste._categorie))
            row.addElement(cat_cell)

            name_cell = TableCell(stylename=style)
            name_cell.addElement(P(text=poste._nom))
            row.addElement(name_cell)

            horaire_cell = TableCell(stylename=style)
            horaire_cell.addElement(P(text=str(poste.get_horaire())))
            row.addElement(horaire_cell)

            benevoles_text = "\n".join(b.get_name() for b in benevoles if b is not None)
            bev_cell = TableCell(stylename=style)
            bev_cell.addElement(P(text=benevoles_text if benevoles_text else "⚠️ Aucun"))
            row.addElement(bev_cell)

            filled_count   = sum(1 for b in benevoles if b is not None)
            capacity_text  = f"{filled_count}/{poste.get_size()}"
            if filled_count == poste.get_size():
                cap_style = self.styles['success']
            elif filled_count == 0:
                cap_style = self.styles['danger']
            else:
                cap_style = self.styles['warning']

            cap_cell = TableCell(stylename=cap_style)
            cap_cell.addElement(P(text=capacity_text))
            row.addElement(cap_cell)
            table.addElement(row)

        self.doc.spreadsheet.addElement(table)

    def _create_calendar_view(self, chromosome: Chromosome) -> None:
        table = Table(name="📅 Vue Calendrier")
        for col_key in ('narrow', 'extra_wide', 'extra_wide', 'extra_wide'):
            table.addElement(TableColumn(stylename=self.column_styles[col_key]))

        header_row = TableRow()
        header_row.addElement(TableCell(stylename=self.styles['header']))
        for jour in ["Vendredi", "Samedi", "Dimanche"]:
            cell = TableCell(stylename=self.styles['header'])
            cell.addElement(P(text=jour))
            header_row.addElement(cell)
        table.addElement(header_row)

        for heure in range(8, 30):
            row = TableRow()
            heure_display = heure if heure < 24 else heure - 24
            heure_cell = TableCell(stylename=self.styles['subheader'])
            heure_cell.addElement(P(text=f"{heure_display}h"))
            row.addElement(heure_cell)

            for jour_idx in [4, 5, 6]:
                postes_matching = [
                    p for p in chromosome.affectations.keys()
                    if (p.get_horaire().get_jour() == jour_idx and
                        p.get_horaire().get_borne_inf() <= heure < p.get_horaire().get_borne_sup())
                ]
                if postes_matching:
                    text = "\n".join(
                        f"• {p._nom} ({sum(1 for b in chromosome.affectations[p] if b is not None)}/{p.get_size()})"
                        for p in postes_matching[:3]
                    )
                    if len(postes_matching) > 3:
                        text += f"\n... +{len(postes_matching) - 3} autres"
                    cell = TableCell(stylename=self.styles['normal'])
                    cell.addElement(P(text=text))
                else:
                    cell = TableCell(stylename=self.styles['alt_row'])
                    cell.addElement(P(text=""))
                row.addElement(cell)

            table.addElement(row)

        self.doc.spreadsheet.addElement(table)

    def _create_legend_sheet(self) -> None:
        table = Table(name="ℹ️ Légende")
        for col_key in ('wide', 'extra_wide', 'medium'):
            table.addElement(TableColumn(stylename=self.column_styles[col_key]))

        title_row  = TableRow()
        title_cell = TableCell(stylename=self.styles['header'], numbercolumnsspanned=3)
        title_cell.addElement(P(text="ℹ️ GUIDE D'UTILISATION"))
        title_row.addElement(title_cell)
        for _ in range(2):
            title_row.addElement(TableCell())
        table.addElement(title_row)
        table.addElement(TableRow())

        explanations = [
            ("📊 Statistiques",           "Vue d'ensemble des affectations"),
            ("👥 Planning par Bénévole",  "Planning personnel de chaque bénévole"),
            ("📋 Affectation par Poste",  "Liste complète des postes et leur staffing"),
            ("📅 Vue Calendrier",         "Grille horaire jour par jour"),
        ]
        for label, desc in explanations:
            row = TableRow()
            lbl = TableCell(stylename=self.styles['subheader'])
            lbl.addElement(P(text=label))
            row.addElement(lbl)
            dsc = TableCell(stylename=self.styles['normal'], numbercolumnsspanned=2)
            dsc.addElement(P(text=desc))
            row.addElement(dsc)
            row.addElement(TableCell())
            table.addElement(row)

        table.addElement(TableRow())

        legend_title_row  = TableRow()
        legend_title_cell = TableCell(stylename=self.styles['subheader'], numbercolumnsspanned=3)
        legend_title_cell.addElement(P(text="🎨 LÉGENDE DES COULEURS"))
        legend_title_row.addElement(legend_title_cell)
        for _ in range(2):
            legend_title_row.addElement(TableCell())
        table.addElement(legend_title_row)

        color_legend = [
            ("Vert",   "Situation OK / Objectif atteint", "success"),
            ("Orange", "Attention requise",                "warning"),
            ("Rouge",  "Problème à résoudre",              "danger"),
            ("Bleu",   "Information importante",           "highlight"),
        ]
        for color_name, meaning, style_key in color_legend:
            row = TableRow()
            color_cell = TableCell(stylename=self.styles[style_key])
            color_cell.addElement(P(text=color_name))
            row.addElement(color_cell)
            meaning_cell = TableCell(stylename=self.styles['normal'], numbercolumnsspanned=2)
            meaning_cell.addElement(P(text=meaning))
            row.addElement(meaning_cell)
            row.addElement(TableCell())
            table.addElement(row)

        self.doc.spreadsheet.addElement(table)

    # ========================================================================
    # UTILITAIRES
    # ========================================================================

    def _organize_by_benevole(self, chromosome: Chromosome) -> dict[str, list]:
        benevole_assignments: dict[str, list] = {}
        for poste, benevoles in chromosome.affectations.items():
            for benevole in benevoles:
                if benevole is None:
                    continue
                benevole_assignments.setdefault(benevole.get_name(), []).append(poste)
        return benevole_assignments

    def _group_by_day(self, postes: list) -> dict[int, list]:
        by_day: dict[int, list] = defaultdict(list)
        for poste in postes:
            by_day[poste.get_horaire().get_jour()].append(poste)
        return by_day

    def _compute_benevole_hours(self, chromosome: Chromosome) -> dict:
        benevole_hours: dict = {}
        for poste, benevoles in chromosome.affectations.items():
            creneau    = poste.get_horaire()
            jour_index = creneau.get_jour() - 4
            duration   = creneau.get_borne_sup() - creneau.get_borne_inf()
            if jour_index < 0 or jour_index > 2:
                continue
            for benevole in benevoles:
                if benevole is None:
                    continue
                if benevole not in benevole_hours:
                    benevole_hours[benevole] = [0, 0, 0]
                benevole_hours[benevole][jour_index] += duration
        return benevole_hours

    def _get_category_style_key(self, cat_id: int) -> str:
        category_map = {
            1: 'cat_bar',          2: 'cat_resto',        3: 'cat_catering',
            4: 'cat_securite',     5: 'cat_prevention',   6: 'cat_ticketterie',
            7: 'cat_camping',      8: 'cat_billetterie',  9: 'cat_animations',
            10: 'cat_accueil',     11: 'cat_acces',       12: 'cat_environnement',
            13: 'cat_logistique',  14: 'cat_technique',
        }
        return category_map.get(cat_id, 'normal')