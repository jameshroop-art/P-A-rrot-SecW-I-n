#!/usr/bin/env python3
"""
Example: Profile a target and generate a report

This example demonstrates basic reconnaissance
"""

import asyncio
from forensicsense.intel.profiler import TargetProfiler
from forensicsense.forensics.report_generator import ReportGenerator


async def main():
    """Profile a target and generate report"""
    
    # Target to profile
    target = "example.com"
    
    print(f"Profiling {target}...")
    
    # Create profiler
    profiler = TargetProfiler()
    
    # Profile target (safe - no exploitation)
    profile = await profiler.profile_target(target, depth='standard')
    
    # Display summary
    print(f"\nProfile complete!")
    print(f"Risk Level: {profile.risk_assessment.get('level', 'UNKNOWN')}")
    print(f"Risk Score: {profile.risk_assessment.get('score', 0)}/100")
    print(f"Open Ports: {len(profile.network_scan.get('open_ports', []))}")
    
    # Generate report
    report_gen = ReportGenerator()
    report_path = report_gen.generate_report(
        profile.to_dict(),
        format='md',
        output_file=f'{target}_report.md'
    )
    
    print(f"\nReport saved to: {report_path}")


if __name__ == '__main__':
    asyncio.run(main())
