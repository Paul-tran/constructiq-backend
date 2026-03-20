from fastapi import APIRouter, HTTPException
from typing import List

from app.models.geography import Site, Location, Unit, Partition
from app.schemas.geography import (
    SiteCreate, SiteUpdate, SiteOut,
    LocationCreate, LocationUpdate, LocationOut,
    UnitCreate, UnitUpdate, UnitOut,
    PartitionCreate, PartitionUpdate, PartitionOut,
)

router = APIRouter(prefix="/geography", tags=["Geography"])


# --- Sites ---

@router.get("/sites", response_model=List[SiteOut])
async def list_sites():
    return await Site.all()


@router.post("/sites", response_model=SiteOut, status_code=201)
async def create_site(data: SiteCreate):
    site = await Site.create(**data.model_dump())
    return site


@router.get("/sites/{site_id}", response_model=SiteOut)
async def get_site(site_id: int):
    site = await Site.get_or_none(id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.patch("/sites/{site_id}", response_model=SiteOut)
async def update_site(site_id: int, data: SiteUpdate):
    site = await Site.get_or_none(id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    await site.update_from_dict(data.model_dump(exclude_none=True)).save()
    return site


@router.delete("/sites/{site_id}", status_code=204)
async def delete_site(site_id: int):
    site = await Site.get_or_none(id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    await site.delete()


# --- Locations ---

@router.get("/sites/{site_id}/locations", response_model=List[LocationOut])
async def list_locations(site_id: int):
    return await Location.filter(site_id=site_id)


@router.post("/locations", response_model=LocationOut, status_code=201)
async def create_location(data: LocationCreate):
    location = await Location.create(**data.model_dump())
    return location


@router.get("/locations/{location_id}", response_model=LocationOut)
async def get_location(location_id: int):
    location = await Location.get_or_none(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.patch("/locations/{location_id}", response_model=LocationOut)
async def update_location(location_id: int, data: LocationUpdate):
    location = await Location.get_or_none(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    await location.update_from_dict(data.model_dump(exclude_none=True)).save()
    return location


@router.delete("/locations/{location_id}", status_code=204)
async def delete_location(location_id: int):
    location = await Location.get_or_none(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    await location.delete()


# --- Units ---

@router.get("/locations/{location_id}/units", response_model=List[UnitOut])
async def list_units(location_id: int):
    return await Unit.filter(location_id=location_id)


@router.post("/units", response_model=UnitOut, status_code=201)
async def create_unit(data: UnitCreate):
    unit = await Unit.create(**data.model_dump())
    return unit


@router.get("/units/{unit_id}", response_model=UnitOut)
async def get_unit(unit_id: int):
    unit = await Unit.get_or_none(id=unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


@router.patch("/units/{unit_id}", response_model=UnitOut)
async def update_unit(unit_id: int, data: UnitUpdate):
    unit = await Unit.get_or_none(id=unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    await unit.update_from_dict(data.model_dump(exclude_none=True)).save()
    return unit


@router.delete("/units/{unit_id}", status_code=204)
async def delete_unit(unit_id: int):
    unit = await Unit.get_or_none(id=unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    await unit.delete()


# --- Partitions ---

@router.get("/units/{unit_id}/partitions", response_model=List[PartitionOut])
async def list_partitions(unit_id: int):
    return await Partition.filter(unit_id=unit_id)


@router.post("/partitions", response_model=PartitionOut, status_code=201)
async def create_partition(data: PartitionCreate):
    partition = await Partition.create(**data.model_dump())
    return partition


@router.get("/partitions/{partition_id}", response_model=PartitionOut)
async def get_partition(partition_id: int):
    partition = await Partition.get_or_none(id=partition_id)
    if not partition:
        raise HTTPException(status_code=404, detail="Partition not found")
    return partition


@router.patch("/partitions/{partition_id}", response_model=PartitionOut)
async def update_partition(partition_id: int, data: PartitionUpdate):
    partition = await Partition.get_or_none(id=partition_id)
    if not partition:
        raise HTTPException(status_code=404, detail="Partition not found")
    await partition.update_from_dict(data.model_dump(exclude_none=True)).save()
    return partition


@router.delete("/partitions/{partition_id}", status_code=204)
async def delete_partition(partition_id: int):
    partition = await Partition.get_or_none(id=partition_id)
    if not partition:
        raise HTTPException(status_code=404, detail="Partition not found")
    await partition.delete()
