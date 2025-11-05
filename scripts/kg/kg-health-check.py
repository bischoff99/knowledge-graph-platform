            for warning in self.warnings:
                print(f"  - {warning}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if self.stats.get('oversized_entities', 0) > 0:
            print("  - Split entities with >12 observations into focused components")
        if self.stats.get('stale_entities', 0) > 0:
            print("  - Review and update entities not verified in 90+ days")
        if self.stats.get('redundant_observations', 0) > 0:
            print("  - Consolidate duplicate observations")
        if self.stats.get('broken_relations', 0) == 0:
            print("  ✅ Graph integrity is excellent - all relations valid")
        
        # Overall health score
        total_issues = len(self.issues) + (len(self.warnings) * 0.5)
        if total_issues == 0:
            health_score = 100
        elif total_issues < 3:
            health_score = 90
        elif total_issues < 7:
            health_score = 75
        else:
            health_score = max(50, 100 - (total_issues * 5))
        
        print(f"\n🏥 OVERALL HEALTH SCORE: {health_score:.0f}%")
        
        if health_score >= 90:
            print("   Status: EXCELLENT ✅")
        elif health_score >= 75:
            print("   Status: GOOD ⚠️")
        else:
            print("   Status: NEEDS ATTENTION ❌")
        
        print("=" * 70)
        return health_score


if __name__ == '__main__':
    # Example usage - in production, fetch from MCP memory
    print("Knowledge Graph Health Check")
    print("Note: Connect to MCP memory server to run full check")
    print("\nUsage:")
    print("  python kg-health-check.py")
    print("\nFeatures:")
    print("  - Entity size validation (5-8 observations optimal)")
    print("  - Broken relation detection")
    print("  - Stale data identification (>90 days)")
    print("  - Redundancy detection")
    print("  - Entity type consistency")
    print("  - Overall health scoring")
