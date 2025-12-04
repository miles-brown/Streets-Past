#!/usr/bin/env python3
"""
Storage Cost Analysis for Historical Map Images & Street Photos
Calculate costs for different image volumes and file sizes across various storage solutions.
"""

import pandas as pd
import json

# Define storage solutions and their pricing
storage_solutions = {
    "Supabase": {
        "free_storage": 1,  # GB
        "free_egress": 5,   # GB/month
        "storage_rate": 0.021,  # $/GB/month after free
        "egress_rate": 0.09,    # $/GB after free
        "max_upload": 50,   # MB
    },
    "Cloudinary": {
        "free_dam_storage": 25,  # GB (DAM free tier)
        "api_credits": 25,      # Monthly credits for API
        "plus_monthly": 99,     # $/month
        "advanced_monthly": 249,  # $/month
        "storage_rate": None,   # Complex credit-based system
    },
    "AWS_S3": {
        "free_storage": 5,   # GB (first year only)
        "standard_rate": 0.023,  # $/GB/month
        "ia_rate": 0.0125,      # $/GB/month (Infrequent Access)
        "free_transfer": 100,   # GB/month (across all AWS services)
        "transfer_rate": 0.09,  # $/GB after free (typical US regions)
    },
    "GitHub_LFS": {
        "free_storage": 10,    # GB
        "free_bandwidth": 10,  # GB/month
        "storage_rate": 0.07,  # $/GB (conversion to GiB)
        "bandwidth_rate": None, # Billed per download
    },
    "Cloudflare_CDN": {
        "free_bandwidth": None,  # Unlimited implied
        "paid_rate": None,      # Custom pricing
        "storage_related": False, # CDN only
    }
}

def calculate_storage_costs(image_volumes, avg_file_sizes_gb):
    """Calculate storage costs for different scenarios"""
    
    scenarios = []
    
    for volume in image_volumes:
        for file_size_gb in avg_file_sizes_gb:
            total_storage_gb = volume * file_size_gb
            total_storage_bytes = total_storage_gb * 1024**3
            total_size_mb = total_storage_gb * 1024
            
            # Calculate monthly transfer scenarios (conservative estimates)
            monthly_views = volume * 2  # Assume 2 views per image per month
            avg_view_size_mb = file_size_gb * 1024 * 0.8  # Assume 80% of original size for viewing
            monthly_transfer_mb = monthly_views * avg_view_size_mb
            monthly_transfer_gb = monthly_transfer_mb / 1024
            
            costs = {}
            
            # Supabase calculations
            if total_storage_gb <= storage_solutions["Supabase"]["free_storage"]:
                supabase_storage_cost = 0
            else:
                supabase_storage_cost = (total_storage_gb - storage_solutions["Supabase"]["free_storage"]) * storage_solutions["Supabase"]["storage_rate"]
            
            if monthly_transfer_gb <= storage_solutions["Supabase"]["free_egress"]:
                supabase_egress_cost = 0
            else:
                supabase_egress_cost = (monthly_transfer_gb - storage_solutions["Supabase"]["free_egress"]) * storage_solutions["Supabase"]["egress_rate"]
            
            supabase_total = supabase_storage_cost + supabase_egress_cost
            costs["Supabase"] = {
                "storage_cost": round(supabase_storage_cost, 2),
                "egress_cost": round(supabase_egress_cost, 2),
                "total_cost": round(supabase_total, 2),
                "fits_free_tier": "Yes" if supabase_total == 0 else "No"
            }
            
            # Cloudinary calculations
            if total_storage_gb <= storage_solutions["Cloudinary"]["free_dam_storage"]:
                cloudinary_option = "Free Tier"
                cloudinary_total = 0
            elif total_storage_gb <= 100:  # Rough estimate for Plus tier
                cloudinary_option = "Plus ($99/month)"
                cloudinary_total = 99
            elif total_storage_gb <= 300:  # Rough estimate for Advanced tier
                cloudinary_option = "Advanced ($249/month)"
                cloudinary_total = 249
            else:
                cloudinary_option = "Enterprise (Custom)"
                cloudinary_total = 500  # Estimated
                
            costs["Cloudinary"] = {
                "tier": cloudinary_option,
                "monthly_cost": cloudinary_total,
                "annual_cost": cloudinary_total * 12,
                "fits_free_tier": "Yes" if cloudinary_total == 0 else "No"
            }
            
            # AWS S3 calculations (only for first year with free tier)
            if total_storage_gb <= storage_solutions["AWS_S3"]["free_storage"]:
                aws_storage_cost = 0
                aws_years = "First Year Only"
            else:
                aws_storage_cost = (total_storage_gb - storage_solutions["AWS_S3"]["free_storage"]) * storage_solutions["AWS_S3"]["standard_rate"]
                aws_years = "Ongoing"
            
            if monthly_transfer_gb <= storage_solutions["AWS_S3"]["free_transfer"]:
                aws_transfer_cost = 0
            else:
                aws_transfer_cost = (monthly_transfer_gb - storage_solutions["AWS_S3"]["free_transfer"]) * storage_solutions["AWS_S3"]["transfer_rate"]
            
            aws_first_year_storage = aws_storage_cost
            aws_ongoing_storage = (total_storage_gb * storage_solutions["AWS_S3"]["standard_rate"])
            aws_first_year_total = aws_first_year_storage + aws_transfer_cost
            aws_ongoing_total = aws_ongoing_storage + aws_transfer_cost
            
            costs["AWS_S3"] = {
                "first_year_monthly": round(aws_first_year_total, 2),
                "first_year_annual": round(aws_first_year_total * 12, 2),
                "ongoing_monthly": round(aws_ongoing_total, 2),
                "ongoing_annual": round(aws_ongoing_total * 12, 2),
                "fits_free_tier": "Yes" if aws_first_year_total == 0 else "No"
            }
            
            # GitHub LFS calculations
            if total_storage_gb <= storage_solutions["GitHub_LFS"]["free_storage"]:
                github_storage_cost = 0
            else:
                github_storage_cost = (total_storage_gb - storage_solutions["GitHub_LFS"]["free_storage"]) * storage_solutions["GitHub_LFS"]["storage_rate"]
            
            github_bandwidth_cost = 0 if monthly_transfer_gb <= storage_solutions["GitHub_LFS"]["free_bandwidth"] else "Variable"
            
            github_total = github_storage_cost
            costs["GitHub_LFS"] = {
                "storage_cost": round(github_storage_cost, 2),
                "bandwidth_cost": github_bandwidth_cost,
                "total_cost": github_total,
                "fits_free_tier": "Yes" if github_storage_cost == 0 else "No"
            }
            
            # Cloudflare CDN (cost depends on origin storage)
            # Assuming origin on one of the above platforms
            cloudflare_cost = "Free tier available"
            
            scenarios.append({
                "volume": volume,
                "file_size_gb": file_size_gb,
                "total_storage_gb": round(total_storage_gb, 2),
                "monthly_transfer_gb": round(monthly_transfer_gb, 2),
                "costs": costs
            })
    
    return scenarios

# Define scenarios
image_volumes = [10000, 50000, 100000]
# Typical image file sizes (in GB)
avg_file_sizes_gb = [0.005, 0.01, 0.02, 0.05]  # 5MB, 10MB, 20MB, 50MB per image

# Calculate costs
cost_analysis = calculate_storage_costs(image_volumes, avg_file_sizes_gb)

# Save results to JSON for further processing
with open('/workspace/docs/storage/cost_analysis_results.json', 'w') as f:
    json.dump(cost_analysis, f, indent=2)

# Create summary tables
summary_data = []

for scenario in cost_analysis:
    row = {
        "Image Count": scenario["volume"],
        "Avg File Size (GB)": scenario["file_size_gb"],
        "Total Storage (GB)": scenario["total_storage_gb"],
        "Monthly Transfer (GB)": scenario["monthly_transfer_gb"]
    }
    
    # Add cost information for each solution
    row["Supabase Monthly ($)"] = scenario["costs"]["Supabase"]["total_cost"]
    row["Cloudinary Tier"] = scenario["costs"]["Cloudinary"]["tier"]
    row["Cloudinary Monthly ($)"] = scenario["costs"]["Cloudinary"]["monthly_cost"]
    row["AWS S3 1st Year ($)"] = scenario["costs"]["AWS_S3"]["first_year_monthly"]
    row["AWS S3 Ongoing ($)"] = scenario["costs"]["AWS_S3"]["ongoing_monthly"]
    row["GitHub LFS Monthly ($)"] = scenario["costs"]["GitHub_LFS"]["total_cost"]
    row["Cloudflare CDN"] = "Free"
    
    summary_data.append(row)

df = pd.DataFrame(summary_data)
df.to_csv('/workspace/docs/storage/cost_comparison.csv', index=False)

print("Storage Cost Analysis Complete!")
print(f"Analyzed {len(cost_analysis)} scenarios")
print("Results saved to:")
print("- cost_analysis_results.json (detailed)")
print("- cost_comparison.csv (summary)")
print("\nSample scenarios:")
for i, scenario in enumerate(cost_analysis[:6]):
    print(f"\nScenario {i+1}: {scenario['volume']} images, {scenario['file_size_gb']} GB avg")
    print(f"  Total Storage: {scenario['total_storage_gb']:.2f} GB")
    print(f"  Supabase: ${scenario['costs']['Supabase']['total_cost']}/month")
    print(f"  Cloudinary: {scenario['costs']['Cloudinary']['tier']}")
    print(f"  AWS S3: ${scenario['costs']['AWS_S3']['ongoing_monthly']}/month (ongoing)")