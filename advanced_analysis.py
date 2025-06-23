import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.decomposition import PCA
import networkx as nx
from itertools import combinations
from collections import defaultdict
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set up visualization style
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 12
sns.set_palette("husl")

class PokemonAdvancedAnalysis:
    """
    A class for performing advanced analysis on the Pokémon dataset.
    Includes team composition analysis, type synergy evaluation, competitive tiering,
    visualization, and machine learning tasks.
    """
    
    def __init__(self, data_path='data/pokemon_engineered.csv'):
        """Initialize with the engineered Pokémon dataset."""
        self.df = pd.read_csv(data_path)
        self.type_colors = {
            'normal': '#A8A77A', 'fire': '#EE8130', 'water': '#6390F0',
            'electric': '#F7D02C', 'grass': '#7AC74C', 'ice': '#96D9D6',
            'fighting': '#C22E28', 'poison': '#A33EA1', 'ground': '#E2BF65',
            'flying': '#A98FF3', 'psychic': '#F95587', 'bug': '#A6B91A',
            'rock': '#B6A136', 'ghost': '#735797', 'dragon': '#6F35FC',
            'dark': '#705746', 'steel': '#B7B7CE', 'fairy': '#D685AD',
            'unknown': '#68A090', 'shadow': '#604E82'
        }
        
        # Type chart for synergy analysis (simplified)
        self.type_chart = self._create_type_chart()
    
    def _create_type_chart(self):
        """Create a type effectiveness chart."""
        # This is a simplified version - in practice, you'd want a complete type chart
        type_chart = {
            'normal': {'rock': 0.5, 'ghost': 0, 'steel': 0.5},
            'fire': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 2, 'bug': 2, 'rock': 0.5, 'dragon': 0.5, 'steel': 2},
            'water': {'fire': 2, 'water': 0.5, 'grass': 0.5, 'ground': 2, 'rock': 2, 'dragon': 0.5},
            # Add more type interactions as needed
        }
        return type_chart
    
    # 1. Visualization Methods
    def plot_type_distribution(self):
        """Plot distribution of primary and secondary types."""
        plt.figure(figsize=(16, 6))
        
        # Primary type distribution
        plt.subplot(1, 2, 1)
        primary_counts = self.df['primary_type'].value_counts()
        primary_colors = [self.type_colors.get(t, '#000000') for t in primary_counts.index]
        sns.barplot(x=primary_counts.values, y=primary_counts.index, palette=primary_colors)
        plt.title('Primary Type Distribution')
        plt.xlabel('Count')
        
        # Secondary type distribution
        plt.subplot(1, 2, 2)
        secondary_counts = self.df['secondary_type'].dropna().value_counts()
        secondary_colors = [self.type_colors.get(t, '#000000') for t in secondary_counts.index]
        sns.barplot(x=secondary_counts.values, y=secondary_counts.index, palette=secondary_colors)
        plt.title('Secondary Type Distribution')
        plt.xlabel('Count')
        
        plt.tight_layout()
        plt.savefig('type_distribution_advanced.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_stat_distribution_by_type(self):
        """Plot distribution of stats grouped by primary type."""
        stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
        
        plt.figure(figsize=(18, 12))
        for i, stat in enumerate(stats, 1):
            plt.subplot(2, 3, i)
            # Get top 10 most common types for better visualization
            top_types = self.df['primary_type'].value_counts().index[:10]
            filtered_df = self.df[self.df['primary_type'].isin(top_types)]
            sns.boxplot(x='primary_type', y=stat, data=filtered_df, 
                       palette=self.type_colors)
            plt.title(f'{stat.title()} by Primary Type')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('stat_distribution_by_type.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_correlation_heatmap(self):
        """Plot correlation heatmap of Pokémon stats."""
        stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed', 'total_stats']
        corr = self.df[stats].corr()
        
        plt.figure(figsize=(12, 8))
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, annot=True, cmap='coolwarm', mask=mask, fmt='.2f', linewidths=0.5)
        plt.title('Pokémon Stats Correlation Heatmap')
        plt.tight_layout()
        plt.savefig('stat_correlations_advanced.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    # 2. Team Composition Analysis
    def analyze_team_composition(self, team_size=6):
        """Analyze and suggest balanced team compositions."""
        # Get top Pokémon by total stats
        top_pokemon = self.df.nlargest(100, 'total_stats')
        
        # Ensure coverage of different types and roles
        team = []
        types_covered = set()
        roles_covered = set()
        
        # Define team roles
        roles = ['physical_attacker', 'special_attacker', 'physical_wall', 
                'special_wall', 'hazard_setter', 'hazard_control']
        
        # Simple role assignment based on stats
        def assign_role(pokemon):
            if pokemon['attack'] > pokemon['special-attack'] * 1.5:
                return 'physical_attacker'
            elif pokemon['special-attack'] > pokemon['attack'] * 1.5:
                return 'special_attacker'
            elif pokemon['defense'] > 100 and pokemon['hp'] > 80:
                return 'physical_wall'
            elif pokemon['special-defense'] > 100 and pokemon['hp'] > 80:
                return 'special_wall'
            elif pokemon['speed'] > 100:
                return 'hazard_control'
            else:
                return 'hazard_setter'
        
        # Sort Pokémon by total stats and try to cover all roles and types
        for _, pokemon in top_pokemon.iterrows():
            if len(team) >= team_size:
                break
                
            role = assign_role(pokemon)
            if role not in roles_covered:
                team.append((pokemon['name'], pokemon['primary_type'], 
                            pokemon.get('secondary_type', 'None'), role))
                types_covered.add(pokemon['primary_type'])
                if pd.notna(pokemon.get('secondary_type')):
                    types_covered.add(pokemon['secondary_type'])
                roles_covered.add(role)
        
        # Create a DataFrame for the team
        team_df = pd.DataFrame(team, columns=['Name', 'Primary Type', 'Secondary Type', 'Role'])
        
        # Save team to CSV
        team_df.to_csv('suggested_team.csv', index=False)
        
        return team_df
    
    # 3. Type Synergy Evaluation
    def evaluate_type_synergy(self, team):
        """Evaluate the type synergy of a given team."""
        team_types = []
        for _, row in team.iterrows():
            team_types.append(row['Primary Type'])
            if pd.notna(row['Secondary Type']) and row['Secondary Type'] != 'None':
                team_types.append(row['Secondary Type'])
        
        # Count type occurrences
        type_counts = pd.Series(team_types).value_counts()
        
        # Check for type redundancy
        redundant_types = type_counts[type_counts > 1].index.tolist()
        
        return {
            'type_diversity': len(set(team_types)) / len(team_types) if team_types else 0,
            'redundant_types': redundant_types,
            'type_coverage': self._calculate_type_coverage(set(team_types))
        }
    
    def _calculate_type_coverage(self, types):
        """Calculate how many types the team is strong against."""
        all_types = set(self.type_colors.keys())
        covered = set()
        
        for t in types:
            if t in self.type_chart:
                for target_type, multiplier in self.type_chart[t].items():
                    if multiplier > 1:  # Super effective
                        covered.add(target_type)
        
        return len(covered) / len(all_types) * 100  # Percentage coverage
    
    # 4. Competitive Tier Classification
    def classify_competitive_tiers(self, n_clusters=5):
        """Classify Pokémon into competitive tiers using K-means clustering."""
        # Select relevant features for tiering
        features = ['total_stats', 'speed', 'attack', 'special-attack', 
                  'defense', 'special-defense', 'hp']
        
        # Scale the features
        scaler = StandardScaler()
        X = scaler.fit_transform(self.df[features])
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.df['tier'] = kmeans.fit_predict(X)
        
        # Sort tiers by average total stats (higher = better)
        tier_order = self.df.groupby('tier')['total_stats'].mean().sort_values(ascending=False).index
        tier_mapping = {old: new for new, old in enumerate(tier_order, 1)}
        self.df['tier'] = self.df['tier'].map(tier_mapping)
        
        # Save the tiered data
        self.df.to_csv('pokemon_with_tiers.csv', index=False)
        
        return self.df[['name', 'primary_type', 'total_stats', 'tier']].sort_values('tier')
    
    # 5. Machine Learning: Type Prediction
    def predict_types(self):
        """Predict Pokémon types based on their stats using Random Forest."""
        # Prepare data
        features = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
        X = self.df[features]
        y = self.df['primary_type']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train the model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Print classification report
        print("\n=== Type Prediction Accuracy ===")
        print(classification_report(y_test, y_pred))
        
        # Get feature importance
        importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n=== Feature Importance ===")
        print(importance)
        
        return model, importance
    
    # 6. Pokémon Clustering
    def cluster_similar_pokemon(self, n_clusters=10):
        """Cluster similar Pokémon based on their stats."""
        # Select relevant features
        features = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
        X = self.df[features]
        
        # Scale the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply PCA for visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Add clusters to the DataFrame
        self.df['cluster'] = clusters
        
        # Plot the clusters
        plt.figure(figsize=(14, 10))
        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', alpha=0.6)
        plt.title('Pokémon Clusters Based on Stats (PCA-reduced)')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.colorbar(scatter, label='Cluster')
        plt.tight_layout()
        plt.savefig('pokemon_clusters.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Save cluster information
        self.df[['name', 'primary_type', 'total_stats', 'cluster']].to_csv('pokemon_clusters.csv', index=False)
        
        return self.df[['name', 'primary_type', 'cluster']].sort_values('cluster')
    
    # 7. Team Recommendation System
    def recommend_team(self, pokemon_name, team_size=6):
        """Recommend a team based on a seed Pokémon."""
        # Find the seed Pokémon
        seed = self.df[self.df['name'].str.lower() == pokemon_name.lower()].iloc[0]
        
        # Get Pokémon that complement the seed
        # For simplicity, we'll look for Pokémon that cover the seed's weaknesses
        team = [seed]
        
        # Add Pokémon that cover the seed's weaknesses
        # This is a simplified version - in practice, you'd use a complete type chart
        recommended_types = []
        if seed['primary_type'] == 'water':
            recommended_types.extend(['electric', 'grass'])
        # Add more type-based recommendations...
        
        # Add Pokémon with recommended types
        for t in recommended_types:
            candidates = self.df[
                (self.df['primary_type'] == t) | 
                (self.df['secondary_type'] == t)
            ].sort_values('total_stats', ascending=False)
            
            if not candidates.empty:
                team.append(candidates.iloc[0])
            
            if len(team) >= team_size:
                break
        
        # Create a DataFrame for the recommended team
        team_df = pd.DataFrame([{
            'name': p['name'],
            'primary_type': p['primary_type'],
            'secondary_type': p.get('secondary_type', 'None'),
            'total_stats': p['total_stats']
        } for p in team])
        
        return team_df

def main():
    """Main function to run the advanced analysis."""
    print("Starting Advanced Pokémon Analysis")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = PokemonAdvancedAnalysis()
    
    # 1. Generate visualizations
    print("\n1. Generating visualizations...")
    analyzer.plot_type_distribution()
    analyzer.plot_stat_distribution_by_type()
    analyzer.plot_correlation_heatmap()
    
    # 2. Team composition analysis
    print("\n2. Analyzing team composition...")
    team = analyzer.analyze_team_composition()
    print("\n=== Suggested Team ===")
    print(team)
    
    # 3. Type synergy evaluation
    print("\n3. Evaluating team synergy...")
    synergy = analyzer.evaluate_type_synergy(team)
    print(f"Type diversity: {synergy['type_diversity']:.2f}")
    print(f"Redundant types: {synergy['redundant_types']}")
    print(f"Type coverage: {synergy['type_coverage']:.1f}%")
    
    # 4. Competitive tier classification
    print("\n4. Classifying Pokémon into competitive tiers...")
    tiers = analyzer.classify_competitive_tiers()
    print("\n=== Top Pokémon by Tier ===")
    for tier, group in tiers.groupby('tier').head(3).groupby('tier'):
        print(f"\nTier {tier}:")
        print(group[['name', 'primary_type', 'total_stats']].to_string(index=False))
    
    # 5. Type prediction with machine learning
    print("\n5. Training type prediction model...")
    model, importance = analyzer.predict_types()
    
    # 6. Clustering similar Pokémon
    print("\n6. Clustering similar Pokémon...")
    clusters = analyzer.cluster_similar_pokemon()
    print("\n=== Sample Clusters ===")
    for cluster, group in clusters.groupby('cluster').head(3).groupby('cluster'):
        print(f"\nCluster {cluster}:")
        print(group[['name', 'primary_type']].to_string(index=False))
    
    # 7. Team recommendation
    print("\n7. Generating team recommendations...")
    recommended_team = analyzer.recommend_team('charizard')
    print("\n=== Recommended Team (based on Charizard) ===")
    print(recommended_team[['name', 'primary_type', 'secondary_type', 'total_stats']].to_string(index=False))
    
    print("\n=== Analysis Complete ===")
    print("Check the generated files for detailed results.")

if __name__ == "__main__":
    main()
