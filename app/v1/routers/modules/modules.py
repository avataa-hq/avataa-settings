from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.database import Database
from v1.database.models.modules import Module
from v1.routers.modules.models import ModuleCreate
from v1.routers.modules.utils import check_source_exists

router = APIRouter(prefix="/modules")


@router.get("/all", status_code=200, tags=["Modules"])
async def read_all_modules(
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    stmt = select(Module)
    all_modules = await session.execute(stmt)
    all_modules = all_modules.scalars().all()
    result = {m.name: m.custom_name for m in all_modules}

    return result


@router.patch("/all", status_code=200, tags=["Modules"])
async def bulk_patch_module(
    modules: dict,
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    stmt = select(Module).where(Module.name.in_(modules.keys()))
    modules_from_db = await session.scalars(stmt)
    modules_from_db = modules_from_db.all()

    # check that custom names are unique
    custom_names_set = set(modules.values())
    if len(custom_names_set) != len(modules.values()):
        raise HTTPException(
            status_code=400, detail="The query contains non-unique custom names"
        )

    stmt = select(Module).where(
        Module.name.not_in(modules.keys()),
        Module.custom_name.in_(modules.values()),
    )
    check_res = await session.scalars(stmt)
    check_res = check_res.all()

    if len(check_res) > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Modules with custom_names={[n.custom_name for n in check_res]}"
            f" already exist!",
        )

    res = dict()
    for modul in modules_from_db:
        modul.custom_name = modules[modul.name]
        session.add(modul)
        res[modul.name] = modul.custom_name
    await session.commit()
    return res


@router.get("/{modul_name}", status_code=200, tags=["Modules"])
async def read_module(
    modul_name: str,
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    module_inst = await check_source_exists(session, modul_name)
    return {module_inst.name: module_inst.custom_name}


@router.patch("/{modul_name}", status_code=200, tags=["Modules"])
async def patch_module(
    modul_name: str,
    custom_name: str,
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    module_inst = await check_source_exists(session, modul_name)
    stmt = select(Module).where(
        Module.custom_name == custom_name, Module.name != modul_name
    )
    module_from_db = await session.execute(stmt)
    module_from_db = module_from_db.first()
    if module_from_db is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Module named '{custom_name}' already exists!",
        )
    module_inst.custom_name = custom_name
    session.add(module_inst)
    await session.commit()
    return {module_inst.name: module_inst.custom_name}


@router.post("/", status_code=201, tags=["DELETE BEFORE PROD"])
async def create_module(
    module_inst: ModuleCreate,
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    """Create Module"""
    stmt = select(Module).where(Module.name == module_inst.name)
    module_from_db = await session.execute(stmt)
    module_from_db = module_from_db.scalars().first()
    if module_from_db:
        raise HTTPException(
            status_code=422,
            detail=f"A module named '{module_inst.name}' already exists!",
        )

    stmt = select(Module).where(Module.custom_name == module_inst.custom_name)
    module_from_db = await session.execute(stmt)
    module_from_db = module_from_db.scalars().first()
    if module_from_db:
        raise HTTPException(
            status_code=422,
            detail=f"Module with custom_name = '{module_inst.custom_name}' already "
            f"exists!",
        )

    module = Module(**module_inst.dict())
    session.add(module)
    await session.commit()
    await session.refresh(module)
    return module


@router.delete("/{modul_name}", status_code=204, tags=["DELETE BEFORE PROD"])
async def delete_module(
    modul_name: str,
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    """Deletes Module by module name"""
    module_inst = await check_source_exists(session, modul_name)
    await session.delete(module_inst)
    await session.commit()
    return {"msg": "Module deleted successfully"}
