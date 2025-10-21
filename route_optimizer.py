import random
import math
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

class RouteOptimizer:
    def __init__(self):
        self.base_location = [-23.5505, -46.6333]  # São Paulo center
        self.avg_speed_kmh = 25  # Average truck speed in urban area
        self.service_time_minutes = 8  # Average time to collect from one bin
    
    def calculate_distance(self, coord1: List[float], coord2: List[float]) -> float:
        """Calculate distance between two GPS coordinates using Haversine formula"""
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth's radius in kilometers
        
        return c * r
    
    def nearest_neighbor_algorithm(self, bins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple nearest neighbor algorithm for route optimization"""
        if not bins:
            return []
        
        # Start from base location
        current_location = self.base_location
        unvisited_bins = bins.copy()
        route = []
        
        while unvisited_bins:
            # Find nearest bin
            nearest_bin = min(
                unvisited_bins,
                key=lambda bin_item: self.calculate_distance(current_location, bin_item['coordinates'])
            )
            
            route.append(nearest_bin)
            current_location = nearest_bin['coordinates']
            unvisited_bins.remove(nearest_bin)
        
        return route
    
    def calculate_route_metrics(self, route: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate route metrics including distance, time, and fuel savings"""
        if not route:
            return {
                'total_distance': 0,
                'estimated_time': 0,
                'fuel_savings': 0,
                'coordinates': [],
                'stops': []
            }
        
        total_distance = 0
        coordinates = [self.base_location]  # Start from base
        current_location = self.base_location
        
        # Calculate distance between consecutive stops
        for bin_item in route:
            bin_coords = bin_item['coordinates']
            distance = self.calculate_distance(current_location, bin_coords)
            total_distance += distance
            coordinates.append(bin_coords)
            current_location = bin_coords
        
        # Return to base
        return_distance = self.calculate_distance(current_location, self.base_location)
        total_distance += return_distance
        coordinates.append(self.base_location)
        
        # Calculate time
        travel_time = (total_distance / self.avg_speed_kmh) * 60  # Convert to minutes
        service_time = len(route) * self.service_time_minutes
        total_time = travel_time + service_time
        
        # Calculate fuel savings compared to non-optimized route
        # Assume non-optimized route is 20-30% longer
        non_optimized_distance = total_distance * random.uniform(1.2, 1.3)
        fuel_savings = ((non_optimized_distance - total_distance) / non_optimized_distance) * 100
        
        return {
            'total_distance': round(total_distance, 1),
            'estimated_time': round(total_time),
            'fuel_savings': round(fuel_savings, 1),
            'coordinates': coordinates,
            'stops': route,
            'travel_time': round(travel_time),
            'service_time': service_time
        }
    
    def calculate_optimal_route(self, bins_for_collection: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate the optimal collection route"""
        if not bins_for_collection:
            return {
                'total_distance': 0,
                'estimated_time': 0,
                'fuel_savings': 0,
                'coordinates': [],
                'stops': []
            }
        
        # Use nearest neighbor algorithm for route optimization
        optimized_route = self.nearest_neighbor_algorithm(bins_for_collection)
        
        # Calculate route metrics
        route_metrics = self.calculate_route_metrics(optimized_route)
        
        # Add estimated collection time for each stop
        for i, stop in enumerate(route_metrics['stops']):
            stop['estimated_time'] = self.service_time_minutes
            stop['sequence'] = i + 1
            stop['arrival_time'] = datetime.now() + timedelta(
                minutes=sum([self.service_time_minutes] * i + 
                           [route_metrics['travel_time'] * (i / len(route_metrics['stops']))])
            )
        
        # Add route summary
        route_metrics.update({
            'route_generated_at': datetime.now().isoformat(),
            'number_of_stops': len(bins_for_collection),
            'optimization_algorithm': 'nearest_neighbor',
            'route_efficiency_score': min(95, 70 + route_metrics['fuel_savings']),  # Score out of 100
        })
        
        return route_metrics
    
    def get_alternative_routes(self, bins_for_collection: List[Dict[str, Any]], num_alternatives: int = 2) -> List[Dict[str, Any]]:
        """Generate alternative route options"""
        alternatives = []
        
        for i in range(num_alternatives):
            # Create variations by shuffling the starting point
            if len(bins_for_collection) > 1:
                shuffled_bins = bins_for_collection.copy()
                random.shuffle(shuffled_bins)
                
                route = self.nearest_neighbor_algorithm(shuffled_bins)
                metrics = self.calculate_route_metrics(route)
                
                alternatives.append({
                    'route_id': f"alt_{i+1}",
                    'description': f"Rota Alternativa {i+1}",
                    **metrics
                })
        
        return alternatives
    
    def optimize_multi_truck_routes(self, bins_for_collection: List[Dict[str, Any]], num_trucks: int = 2) -> List[Dict[str, Any]]:
        """Optimize routes for multiple trucks"""
        if not bins_for_collection or num_trucks <= 0:
            return []
        
        # Simple division of bins among trucks
        bins_per_truck = len(bins_for_collection) // num_trucks
        truck_routes = []
        
        for truck_id in range(num_trucks):
            start_idx = truck_id * bins_per_truck
            if truck_id == num_trucks - 1:  # Last truck takes remaining bins
                truck_bins = bins_for_collection[start_idx:]
            else:
                truck_bins = bins_for_collection[start_idx:start_idx + bins_per_truck]
            
            if truck_bins:
                route_metrics = self.calculate_optimal_route(truck_bins)
                route_metrics.update({
                    'truck_id': f"truck_{truck_id + 1}",
                    'truck_name': f"Caminhão {truck_id + 1}",
                    'driver': f"Motorista {truck_id + 1}"
                })
                truck_routes.append(route_metrics)
        
        return truck_routes
    
    def calculate_environmental_impact(self, route_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate environmental impact of the optimized route"""
        total_distance = route_metrics.get('total_distance', 0)
        fuel_savings_percent = route_metrics.get('fuel_savings', 0)
        
        # Estimates based on typical truck consumption
        fuel_consumption_per_km = 0.35  # liters per km
        co2_per_liter = 2.7  # kg CO2 per liter of diesel
        
        fuel_consumed = total_distance * fuel_consumption_per_km
        fuel_saved = fuel_consumed * (fuel_savings_percent / 100)
        
        co2_emitted = fuel_consumed * co2_per_liter
        co2_saved = fuel_saved * co2_per_liter
        
        return {
            'fuel_consumed_liters': round(fuel_consumed, 2),
            'fuel_saved_liters': round(fuel_saved, 2),
            'co2_emitted_kg': round(co2_emitted, 2),
            'co2_saved_kg': round(co2_saved, 2),
            'environmental_score': min(100, 50 + fuel_savings_percent * 2)  # Score out of 100
        }
    
    def get_route_statistics(self, route_metrics: Dict[str, Any]) -> Dict[str, str]:
        """Get formatted route statistics for display"""
        environmental_impact = self.calculate_environmental_impact(route_metrics)
        
        return {
            'distance': f"{route_metrics.get('total_distance', 0)} km",
            'time': f"{route_metrics.get('estimated_time', 0)} min",
            'stops': f"{route_metrics.get('number_of_stops', 0)} paradas",
            'efficiency': f"{route_metrics.get('route_efficiency_score', 0)}%",
            'fuel_savings': f"{route_metrics.get('fuel_savings', 0)}%",
            'co2_saved': f"{environmental_impact['co2_saved_kg']} kg CO₂"
        }
