import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from pathlib import Path
import io
import base64

def create_simulation_plot(grid: np.ndarray, title: str = "Crowd Simulation") -> plt.Figure:
    """Create a matplotlib plot for the simulation grid with labels"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create custom colormap for different elements
    from matplotlib.colors import ListedColormap, BoundaryNorm
    
    # Define colors: open space, walls, destinations, entry gates, exit gates, attendees
    colors = ['white', 'black', 'blue', 'green', 'orange', '#ff6666', '#ff3333', '#ff0000', '#cc0000', '#990000']
    cmap = ListedColormap(colors)
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]
    norm = BoundaryNorm(bounds, cmap.N)
    
    # Process grid for visualization
    vis_grid = grid.copy()
    vis_grid[vis_grid == -1] = -1  # Keep walls as -1
    
    im = ax.imshow(vis_grid, cmap=cmap, norm=norm, interpolation='nearest')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Y Position')
    ax.set_ylabel('X Position')
    
    # Add legend
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', label='Open Space'),
        plt.Rectangle((0,0),1,1, facecolor='black', label='Wall-Obstacle'),
        plt.Rectangle((0,0),1,1, facecolor='blue', label='Destinations'),
        plt.Rectangle((0,0),1,1, facecolor='green', label='Entry Gates'),
        plt.Rectangle((0,0),1,1, facecolor='orange', label='Exit Gates'),
        plt.Rectangle((0,0),1,1, facecolor='#ff6666', label='Attendees (Low Density)'),
        plt.Rectangle((0,0),1,1, facecolor='#cc0000', label='Attendees (High Density)')
    ]
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    return fig

def create_heatmap(grid: np.ndarray, filename: str, title: str = "Congestion Heatmap") -> str:
    """Create and save a heatmap image for before/after comparison"""
    fig = create_simulation_plot(grid, title)
    
    # Save to file
    output_path = Path(__file__).parent.parent.parent / "temp" / filename
    output_path.parent.mkdir(exist_ok=True)
    
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    return str(output_path)

def create_metrics_comparison_chart(before_metrics, after_metrics) -> plt.Figure:
    """Create a comparison chart showing before vs after metrics"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Wait time comparison
    categories = ['Before AI', 'After AI']
    wait_times = [before_metrics.avg_wait_time_mins, after_metrics.avg_wait_time_mins]
    colors = ['#ff4444', '#44ff44']
    
    bars1 = ax1.bar(categories, wait_times, color=colors, alpha=0.7)
    ax1.set_title('Average Wait Time', fontweight='bold')
    ax1.set_ylabel('Minutes')
    ax1.set_ylim(0, max(wait_times) * 1.2)
    
    # Add value labels on bars
    for bar, value in zip(bars1, wait_times):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{value} min', ha='center', va='bottom', fontweight='bold')
    
    # Congestion comparison
    congestion_pct = [before_metrics.peak_congestion_percent * 100, 
                     after_metrics.peak_congestion_percent * 100]
    
    bars2 = ax2.bar(categories, congestion_pct, color=colors, alpha=0.7)
    ax2.set_title('Peak Congestion', fontweight='bold')
    ax2.set_ylabel('Percentage (%)')
    ax2.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar, value in zip(bars2, congestion_pct):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig

def grid_to_base64_image(grid: np.ndarray, title: str = "") -> str:
    """Convert grid to base64 encoded image for Streamlit display"""
    fig = create_simulation_plot(grid, title)
    
    # Convert to base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"

class SimulationAnimator:
    """Handle real-time animation of simulation steps"""
    
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.im = None
        
    def update_frame(self, grid: np.ndarray):
        """Update the animation frame with new grid data"""
        self.ax.clear()
        
        # Use same visualization as static plot
        from matplotlib.colors import ListedColormap, BoundaryNorm
        
        colors = ['white', 'black', 'blue', 'green', 'orange', '#ff6666', '#ff3333', '#ff0000', '#cc0000', '#990000']
        cmap = ListedColormap(colors)
        bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]
        norm = BoundaryNorm(bounds, cmap.N)
        
        vis_grid = grid.copy()
        vis_grid[vis_grid == -1] = -1
        
        self.im = self.ax.imshow(vis_grid, cmap=cmap, norm=norm, 
                                interpolation='nearest', animated=True)
        
        self.ax.set_title('Live Simulation', fontweight='bold')
        
        return [self.im]