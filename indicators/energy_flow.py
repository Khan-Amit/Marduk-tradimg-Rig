#!/usr/bin/env python3
# ============================================================
# ⚡ ENERGY FLOW - 3-6-9 Sacred Node Detection
# ============================================================
#
# Detects 3-6-9 energy nodes in market data
# Identifies vortex patterns and calculates confluence
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EnergyFlow:
    """
    Energy Flow Indicator
    
    Detects 3-6-9 energy nodes in market data:
    - Nodes: 3:00, 6:00, 9:00 (UTC/EST)
    - Vortex: Range reduces to 3, 6, or 9
    - Confluence: C3 (single touch) → C18 (full alignment)
    """
    
    # Sacred nodes (hours)
    SACRED_NODES = [3, 6, 9]
    
    # Node labels
    NODE_LABELS = {
        3: '3:00 AM/PM',
        6: '6:00 AM/PM',
        9: '9:00 AM/PM'
    }
    
    def __init__(self):
        self.name = "Energy Flow"
        self.version = "1.0.0"
        self.nodes = self.SACRED_NODES
        
        logger.info(f"⚡ {self.name} v{self.version} initialized")
        logger.info(f"   Sacred Nodes: {self.nodes}")
    
    def detect_nodes(self, timestamps: pd.DatetimeIndex) -> Dict:
        """
        Detect 3-6-9 energy nodes in timestamp data
        
        Args:
            timestamps: Pandas DatetimeIndex of market data
            
        Returns:
            Dict with node detection results
        """
        results = {}
        
        for node in self.nodes:
            # Filter timestamps at node hours
            node_mask = timestamps.hour == node
            node_times = timestamps[node_mask]
            
            if len(node_times) > 0:
                results[node] = {
                    'count': len(node_times),
                    'times': node_times.tolist(),
                    'first': node_times[0],
                    'last': node_times[-1],
                    'label': self.NODE_LABELS.get(node, f'{node}:00')
                }
            else:
                results[node] = {
                    'count': 0,
                    'times': [],
                    'first': None,
                    'last': None,
                    'label': self.NODE_LABELS.get(node, f'{node}:00')
                }
        
        return results
    
    def detect_vortex(self, price_data: pd.Series) -> Dict:
        """
        Detect vortex patterns in price data
        
        Args:
            price_data: Price series
            
        Returns:
            Vortex detection results
        """
        # Calculate price range
        price_range = price_data.max() - price_data.min()
        range_percent = (price_range / price_data.mean()) * 100
        
        # Check if range reduces to 3, 6, or 9
        vortex_detected = False
        vortex_node = None
        vortex_strength = 0
        
        for node in self.nodes:
            # Check if range is close to node value
            if abs(range_percent - node) < 0.5:
                vortex_detected = True
                vortex_node = node
                vortex_strength = 1 - (abs(range_percent - node) / 5)
                break
            
            # Check if range is multiple of node
            if range_percent > 0 and range_percent % node < 0.5:
                vortex_detected = True
                vortex_node = node
                vortex_strength = 0.8
                break
        
        # Additional vortex characteristics
        volatility = price_data.pct_change().std() * 100
        
        return {
            'detected': vortex_detected,
            'node': vortex_node,
            'strength': round(vortex_strength, 2),
            'range_percent': round(range_percent, 2),
            'volatility': round(volatility, 2),
            'range': round(price_range, 5),
            'mean_price': round(price_data.mean(), 5)
        }
    
    def calculate_confluence(
        self,
        current_price: float,
        nodes: Dict,
        price_data: pd.Series
    ) -> Dict:
        """
        Calculate confluence score (C3-C18)
        
        Args:
            current_price: Current market price
            nodes: Node detection results
            price_data: Historical price data
            
        Returns:
            Confluence score and details
        """
        score = 0
        details = []
        components = []
        
        # 1. Node presence (C3 per node)
        node_count = 0
        for node, data in nodes.items():
            if data['count'] > 0:
                node_count += 1
                score += 3
                details.append(f"Node {node} present")
                components.append({'node': node, 'score': 3, 'reason': 'Node active'})
        
        # 2. Node alignment (price near node levels)
        node_alignment = 0
        for node, data in nodes.items():
            if data['count'] > 0 and data['times']:
                # Get price at node times
                node_prices = []
                for t in data['times']:
                    idx = price_data.index.get_loc(t, method='nearest')
                    if idx is not None:
                        node_prices.append(price_data.iloc[idx])
                
                if node_prices:
                    avg_node_price = np.mean(node_prices)
                    price_diff = abs(current_price - avg_node_price) / current_price
                    
                    if price_diff < 0.001:  # Within 0.1%
                        score += 3
                        node_alignment += 1
                        details.append(f"Price aligned with node {node}")
                        components.append({
                            'node': node,
                            'score': 3,
                            'reason': 'Price alignment'
                        })
        
        # 3. Vortex detection
        vortex = self.detect_vortex(price_data)
        if vortex['detected']:
            score += 3
            details.append(f"Vortex detected at node {vortex['node']}")
            components.append({
                'node': vortex['node'],
                'score': 3,
                'reason': 'Vortex detected'
            })
        
        # 4. Fibonacci alignment (from QuantumEngine)
        # This is calculated externally and added as bonus
        
        # Calculate confluence level
        if score >= 15:
            level = 'C18'  # Full alignment
            description = 'Full 3-6-9 alignment with vortex and fib'
        elif score >= 12:
            level = 'C15'
            description = 'Strong alignment with vortex'
        elif score >= 9:
            level = 'C12'
            description = 'Multiple nodes with vortex'
        elif score >= 6:
            level = 'C9'
            description = 'Three nodes active'
        elif score >= 3:
            level = 'C6'
            description = 'Two nodes active'
        else:
            level = 'C3'
            description = 'Single node active'
        
        return {
            'score': score,
            'level': level,
            'description': description,
            'node_count': node_count,
            'node_alignment': node_alignment,
            'vortex': vortex['detected'],
            'details': details,
            'components': components,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_node_energy(self, nodes: Dict) -> Dict:
        """
        Calculate energy level for each node
        
        Args:
            nodes: Node detection results
            
        Returns:
            Energy levels for each node
        """
        energy = {}
        
        for node, data in nodes.items():
            if data['count'] > 0:
                # Energy based on frequency and recency
                frequency = min(data['count'] / 10, 1.0)
                
                # Recency bonus (recent nodes have higher energy)
                if data['last']:
                    hours_since = (datetime.now() - data['last']).total_seconds() / 3600
                    recency = max(0, 1 - (hours_since / 24))
                else:
                    recency = 0
                
                energy[node] = {
                    'frequency': round(frequency, 2),
                    'recency': round(recency, 2),
                    'energy': round((frequency * 0.6 + recency * 0.4), 2),
                    'label': data['label'],
                    'count': data['count']
                }
            else:
                energy[node] = {
                    'frequency': 0,
                    'recency': 0,
                    'energy': 0,
                    'label': data['label'],
                    'count': 0
                }
        
        return energy
    
    def analyze(self, price_data: pd.DataFrame) -> Dict:
        """
        Complete energy flow analysis
        
        Args:
            price_data: DataFrame with OHLC data
            
        Returns:
            Complete energy flow analysis
        """
        if price_data.empty:
            return {'error': 'No data provided'}
        
        timestamps = price_data.index
        close_prices = price_data['close']
        current_price = close_prices.iloc[-1]
        
        # Detect nodes
        nodes = self.detect_nodes(timestamps)
        
        # Detect vortex
        vortex = self.detect_vortex(close_prices)
        
        # Calculate confluence
        confluence = self.calculate_confluence(
            current_price,
            nodes,
            close_prices
        )
        
        # Get node energy
        energy = self.get_node_energy(nodes)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_price': current_price,
            'nodes': nodes,
            'vortex': vortex,
            'confluence': confluence,
            'energy': energy,
            'summary': {
                'total_energy': round(sum(e['energy'] for e in energy.values()), 2),
                'active_nodes': sum(1 for e in energy.values() if e['energy'] > 0.5),
                'vortex_detected': vortex['detected']
            }
        }


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Energy Flow indicator
    energy = EnergyFlow()
    
    # Create sample data
    dates = pd.date_range(start='2026-06-23', periods=100, freq='1H')
    np.random.seed(42)
    prices = 1.32000 + np.cumsum(np.random.randn(100) * 0.001)
    
    df = pd.DataFrame({
        'close': prices,
        'high': prices + 0.001,
        'low': prices - 0.001
    }, index=dates)
    
    # Analyze
    result = energy.analyze(df)
    
    print("\n" + "="*60)
    print("⚡ ENERGY FLOW ANALYSIS RESULT")
    print("="*60)
    print(f"  📍 Current Price: {result['current_price']:.5f}")
    print(f"  🌀 Confluence: {result['confluence']['level']}")
    print(f"  📊 Score: {result['confluence']['score']}/18")
    print(f"  🔄 Vortex: {result['vortex']['detected']}")
    print(f"  📈 Total Energy: {result['summary']['total_energy']}")
    print(f"  📋 Active Nodes: {result['summary']['active_nodes']}")
    print("="*60)
