import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict
from src.data_manager import DataManager
from src.ranking_calculator import RankingCalculator

class AdvancementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("East Bay League Tournament - Advancement Calculator")
        self.root.geometry("1000x800")
        
        self.data_manager = DataManager()
        self.ranking_calculator = RankingCalculator()
        
        # State for manual inputs
        self.alliance_selections: Dict[str, int] = {} # Team -> Alliance Rank (1-4)
        self.awards: Dict[str, int] = {} # Team -> Points
        self.playoff_results: Dict[str, int] = {} # Team -> Points
        
        # Setup GUI
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self._setup_standings_tab()
        self._setup_match_entry_tab()
        self._setup_advancement_tab()
        
        self.refresh_standings()

    def _setup_standings_tab(self):
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="League Standings")
        
        # Treeview
        columns = ("rank", "number", "name", "total_rp", "matches")
        self.tree_standings = ttk.Treeview(self.tab1, columns=columns, show="headings", height=20)
        
        self.tree_standings.heading("rank", text="Rank")
        self.tree_standings.heading("number", text="Team #")
        self.tree_standings.heading("name", text="Team Name")
        self.tree_standings.heading("total_rp", text="Total RP (Top 10)")
        self.tree_standings.heading("matches", text="Matches Played")
        
        self.tree_standings.column("rank", width=50, anchor="center")
        self.tree_standings.column("number", width=80, anchor="center")
        self.tree_standings.column("name", width=250)
        self.tree_standings.column("total_rp", width=100, anchor="center")
        self.tree_standings.column("matches", width=100, anchor="center")
        
        self.tree_standings.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tag configuration for highlighting
        self.tree_standings.tag_configure("highlight", background="#e6f3ff") # Light blue for user team
        
    def _setup_match_entry_tab(self):
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Tournament Match Entry")
        
        frame = ttk.LabelFrame(self.tab2, text="Enter Tournament Match Result")
        frame.pack(padx=20, pady=20, fill="x")
        
        grid_opts = {'padx': 5, 'pady': 5}
        
        # Match ID
        ttk.Label(frame, text="Match ID (e.g. T-1):").grid(row=0, column=0, **grid_opts)
        self.entry_match_id = ttk.Entry(frame)
        self.entry_match_id.grid(row=0, column=1, **grid_opts)
        
        # Red Alliance
        ttk.Label(frame, text="Red 1 Team #:").grid(row=1, column=0, **grid_opts)
        self.entry_r1 = ttk.Entry(frame)
        self.entry_r1.grid(row=1, column=1, **grid_opts)
        
        ttk.Label(frame, text="Red 2 Team #:").grid(row=2, column=0, **grid_opts)
        self.entry_r2 = ttk.Entry(frame)
        self.entry_r2.grid(row=2, column=1, **grid_opts)
        
        ttk.Label(frame, text="Red Score:").grid(row=3, column=0, **grid_opts)
        self.entry_r_score = ttk.Entry(frame)
        self.entry_r_score.grid(row=3, column=1, **grid_opts)
        
        ttk.Label(frame, text="Red RP (Dots):").grid(row=4, column=0, **grid_opts)
        self.entry_r_rp = ttk.Entry(frame)
        self.entry_r_rp.grid(row=4, column=1, **grid_opts)
        
        # Blue Alliance
        ttk.Label(frame, text="Blue 1 Team #:").grid(row=1, column=2, **grid_opts)
        self.entry_b1 = ttk.Entry(frame)
        self.entry_b1.grid(row=1, column=3, **grid_opts)
        
        ttk.Label(frame, text="Blue 2 Team #:").grid(row=2, column=2, **grid_opts)
        self.entry_b2 = ttk.Entry(frame)
        self.entry_b2.grid(row=2, column=3, **grid_opts)
        
        ttk.Label(frame, text="Blue Score:").grid(row=3, column=2, **grid_opts)
        self.entry_b_score = ttk.Entry(frame)
        self.entry_b_score.grid(row=3, column=3, **grid_opts)
        
        ttk.Label(frame, text="Blue RP (Dots):").grid(row=4, column=2, **grid_opts)
        self.entry_b_rp = ttk.Entry(frame)
        self.entry_b_rp.grid(row=4, column=3, **grid_opts)
        
        # Valid Teams Helper
        teams_str = ", ".join(sorted(self.data_manager.teams.keys()))
        ttk.Label(self.tab2, text=f"Valid Teams: {teams_str}", wraplength=800).pack(pady=10)
        
        # Checkbox for Surrogate? Maybe later.
        
        # Submit
        btn = ttk.Button(frame, text="Add Match & Update Rankings", command=self.add_match)
        btn.grid(row=5, column=0, columnspan=4, pady=20)
        
    def _setup_advancement_tab(self):
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Advancement & Awards")
        
        # Top Panel: Inputs
        frame_inputs = ttk.Frame(self.tab3)
        frame_inputs.pack(fill='x', padx=10, pady=10)
        
        # Awards Section
        lf_awards = ttk.LabelFrame(frame_inputs, text="Input Awards & Alliance Results")
        lf_awards.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(lf_awards, text="Team #:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_adv_team = ttk.Entry(lf_awards, width=10)
        self.entry_adv_team.grid(row=0, column=1, padx=5, pady=5)
        
        self.var_award_type = tk.StringVar(value="Inspire 1 (60)")
        options = [
            "Inspire 1 (60)", "Inspire 2 (50)", "Inspire 3 (40)",
            "Think/Connect/etc 1 (45)", "Think/Connect/etc 2 (35)", "Think/Connect/etc 3 (30)",
            "Design 1 (35)", "Design 2 (30)", "Design 3 (25)",
            "Judges Choice (25)",
            "Alliance 1 Captain (20)", "Alliance 2 Captain (19)", 
            "Alliance 3 Captain (18)", "Alliance 4 Captain (17)",
            "Winning Alliance (40)", "Finalist Alliance (20)"
        ]
        
        opt_menu = ttk.OptionMenu(lf_awards, self.var_award_type, options[0], *options)
        opt_menu.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(lf_awards, text="Add Points", command=self.add_advancement_points).grid(row=0, column=3, padx=5, pady=5)
        
        # List of added points
        self.list_points = tk.Listbox(lf_awards, height=6)
        self.list_points.grid(row=1, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
        
        # Refresh Button
        ttk.Button(frame_inputs, text="Calculate Advancement", command=self.refresh_advancement).pack(pady=10)
        
        # Results Table
        columns = ("rank", "number", "name", "qual_pts", "alliance_pts", "award_pts", "playoff_pts", "total_ap")
        self.tree_adv = ttk.Treeview(self.tab3, columns=columns, show="headings")
        
        self.tree_adv.heading("rank", text="Rank")
        self.tree_adv.heading("number", text="Team #")
        self.tree_adv.heading("name", text="Name")
        self.tree_adv.heading("qual_pts", text="Qual Pts")
        self.tree_adv.heading("alliance_pts", text="Alliance Pts")
        self.tree_adv.heading("award_pts", text="Award Pts")
        self.tree_adv.heading("playoff_pts", text="Playoff Pts")
        self.tree_adv.heading("total_ap", text="TOTAL AP")
        
        self.tree_adv.column("rank", width=50, anchor="center")
        self.tree_adv.column("number", width=70, anchor="center")
        self.tree_adv.column("name", width=150)
        self.tree_adv.column("qual_pts", width=70, anchor="center")
        self.tree_adv.column("alliance_pts", width=80, anchor="center")
        self.tree_adv.column("award_pts", width=70, anchor="center")
        self.tree_adv.column("playoff_pts", width=70, anchor="center")
        self.tree_adv.column("total_ap", width=80, anchor="center")
        
        self.tree_adv.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tree_adv.tag_configure("advance", background="#c6efce") # Green for Advancing
        self.tree_adv.tag_configure("highlight", background="#e6f3ff") # Blue for User

    def refresh_standings(self):
        # Clear existing
        for item in self.tree_standings.get_children():
            self.tree_standings.delete(item)
            
        teams = self.data_manager.get_all_teams()
        sorted_teams = self.ranking_calculator.calculate_league_rankings(teams)
        
        for team in sorted_teams:
            tags = ()
            if team.number == "14259":
                tags = ("highlight",)
            
            self.tree_standings.insert("", "end", values=(
                team.league_rank, 
                team.number, 
                team.name, 
                team.total_rp, 
                team.matches_played
            ), tags=tags)
            
        # Also refresh advancement to update Ranking Points there
        self.refresh_advancement()

    def add_match(self):
        mid = self.entry_match_id.get()
        r1 = self.entry_r1.get()
        r2 = self.entry_r2.get()
        b1 = self.entry_b1.get()
        b2 = self.entry_b2.get()
        try:
            rs = int(self.entry_r_score.get())
            bs = int(self.entry_b_score.get())
            rrp = int(self.entry_r_rp.get())
            brp = int(self.entry_b_rp.get())
        except ValueError:
            messagebox.showerror("Error", "Scores and RPs must be integers")
            return
            
        self.data_manager.add_tournament_match(mid, r1, r2, b1, b2, rs, bs, rrp, brp)
        messagebox.showinfo("Success", f"Match {mid} added!")
        self.refresh_standings()
        
        # Clear fields
        self.entry_match_id.delete(0, tk.END)
        # self.entry_r_score.delete(0, tk.END) # Keep teams for convenience? No.
        
    def add_advancement_points(self):
        team = self.entry_adv_team.get()
        selection = self.var_award_type.get()
        
        if team not in self.data_manager.teams:
            messagebox.showerror("Error", f"Team {team} not found")
            return
            
        pts = int(re.search(r'\((\d+)\)', selection).group(1))
        
        # Logic to route into correct dictionary
        if "Alliance" in selection and "Captain" in selection:
            # e.g. "Alliance 1 Captain (20)" -> Rank 1
            rank = int(re.search(r'Alliance (\d)', selection).group(1))
            self.alliance_selections[team] = rank
            desc = f"Alliance {rank} Cap/Sel"
        elif "Winning Alliance" in selection:
            self.playoff_results[team] = pts
            desc = "Playoff Winner"
        elif "Finalist Alliance" in selection:
            self.playoff_results[team] = pts
            desc = "Playoff Finalist"
        else:
            # Awards
            current = self.awards.get(team, 0)
            self.awards[team] = current + pts
            desc = f"{selection.split('(')[0].strip()}"
            
        self.list_points.insert(tk.END, f"Team {team}: {desc} (+{pts})")
        
    def refresh_advancement(self):
        for item in self.tree_adv.get_children():
            self.tree_adv.delete(item)
            
        teams = self.data_manager.get_all_teams()
        # Ensure rankings are up to date
        ranked_teams = self.ranking_calculator.calculate_league_rankings(teams)
        
        final_teams = self.ranking_calculator.calculate_advancement_points(
            ranked_teams,
            self.alliance_selections,
            self.awards,
            self.playoff_results
        )
        
        # Top 2 Advance
        for i, team in enumerate(final_teams):
            rank = i + 1
            qual_pts = max(2, 17 - team.league_rank)
            
            # Recalculate component points for display
            all_pts = 0
            if team.number in self.alliance_selections:
                all_pts = 21 - self.alliance_selections[team.number]
            
            award_pts = self.awards.get(team.number, 0)
            play_pts = self.playoff_results.get(team.number, 0)
            
            tags = []
            if rank <= 2:
                tags.append("advance")
            if team.number == "14259":
                tags.append("highlight")
            
            self.tree_adv.insert("", "end", values=(
                rank,
                team.number,
                team.name,
                qual_pts,
                all_pts,
                award_pts,
                play_pts,
                team.advancement_points
            ), tags=tuple(tags))
            
import re
