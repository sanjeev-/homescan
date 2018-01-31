from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Property(models.Model):
    """A property that may or may not be on the market for sale.
    Not tied to specific users.
    """
    # ============= Address =============
    street_address_1 = models.CharField(max_length=191)
    street_address_2 = models.CharField(max_length=191, blank=True, null=True)
    city = models.CharField(max_length=191)
    state = models.CharField(max_length=191)
    zip_code = models.CharField(max_length=15)
    latitude = models.FloatField(blank=True,null=True)
    longitude = models.FloatField(blank=True,null=True)
    # ============= Address keys =============
    # House Canary slug is capitalized e.g. '16-Meadow-Ln-Pelham-NH-41239'
    hc_slug = models.SlugField(max_length=191, unique=True) # Has db_index by default.
    # Internal lowercase slug e.g. '16-meadow-ln-pelham-nh-41239'
    lowercase_slug = models.SlugField(max_length=191) # Has db_index by default.

    # ============= Listing data =============
    list_price = models.BigIntegerField(blank=True, null=True)
    num_bedrooms = models.DecimalField(
        max_digits=5, decimal_places=1, blank=True, null=True)
    num_bathrooms = models.DecimalField(
        max_digits=5, decimal_places=1, blank=True, null=True)
    building_area_sq_ft = models.PositiveIntegerField(blank=True, null=True)
    home_type = models.CharField(max_length=280,blank=True,null=True)
    

    # ============= Valuation =============
    # Ribbon guaranteed max bid for property, assuming enough Buying Power.
    certified_max_bid = models.BigIntegerField(null=True, blank=True)
    certified_max_bid_created_at = models.DateTimeField(null=True, blank=True)

    house_canary_avm = models.BigIntegerField(null=True, blank=True)
    red_bell_ave = models.BigIntegerField(null=True, blank=True)
    red_bell_ar_bpo = models.BigIntegerField(null=True, blank=True)
    red_bell_bpo = models.PositiveIntegerField(blank=True, null=True)
    
    # ============= Features =============
    
    num_floors = models.PositiveIntegerField(blank=True, null=True)
    year_built = models.PositiveIntegerField(blank=True, null=True)
    listing_status = models.CharField(max_length=280, blank=True, null=True)
    flooring = models.CharField(max_length=280, blank=True, null=True)
    interior_features = models.CharField(max_length=280, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)
    subdivision = models.CharField(max_length=280, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_foreclosure = models.NullBooleanField(blank=True, null=True)
    has_septic = models.NullBooleanField(blank=True, null=True)
    has_pool = models.NullBooleanField(blank=True, null=True)
    has_established_subdivision = models.NullBooleanField(blank=True, null=True)
    has_well = models.NullBooleanField(blank=True, null=True)
    has_garage = models.NullBooleanField(blank=True, null=True)
    no_pool_well_septic = models.NullBooleanField(blank=True, null=True)
    num_half_bath = models.PositiveIntegerField(blank=True, null=True)
    school_score = models.PositiveIntegerField(blank=True, null=True)
    days_on_site = models.PositiveIntegerField(blank=True, null=True)
    start_date_on_site = models.CharField(max_length=280, blank=True, null=True)
    garage_detail = models.PositiveIntegerField(blank=True, null=True)
    num_full_bath = models.PositiveIntegerField(blank=True, null=True)
    MLS = models.BigIntegerField(blank=True, null=True)
    
    # =========== ImageInfo ===========
    
    img_path_header = models.CharField(max_length=280, blank=True, null=True)
    img_paths_gallery = models.TextField(blank=True, null=True)
    
    
    
    

    class Meta:
        verbose_name_plural = 'Properties'

    def __str__(self):
        return '%s, %s, %s, %s %s. Max bid %s' % (
            self.street_address_1,
            self.street_address_2,
            self.city,
            self.state,
            self.zip_code,
            self.certified_max_bid,
        )
