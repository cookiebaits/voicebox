"""Post-migration data seeding and backfills."""

import json
import logging
import uuid
import os
import shutil

from .. import config

logger = logging.getLogger(__name__)


def backfill_generation_versions(SessionLocal, Generation, GenerationVersion) -> None:
    """Create 'clean' version entries for generations that predate the versions feature."""
    db = SessionLocal()
    try:
        existing_version_gen_ids = {
            row[0] for row in db.query(GenerationVersion.generation_id).all()
        }
        generations = db.query(Generation).filter(
            Generation.status == "completed",
            Generation.audio_path.isnot(None),
            Generation.audio_path != "",
        ).all()

        count = 0
        for gen in generations:
            if gen.id in existing_version_gen_ids:
                continue
            resolved_audio_path = config.resolve_storage_path(gen.audio_path)
            if resolved_audio_path is None or not resolved_audio_path.exists():
                continue
            version = GenerationVersion(
                id=str(uuid.uuid4()),
                generation_id=gen.id,
                label="clean",
                audio_path=gen.audio_path,
                effects_chain=None,
                is_default=True,
            )
            db.add(version)
            count += 1

        if count > 0:
            db.commit()
            logger.info("Backfilled %d generation version entries", count)
    finally:
        db.close()


def seed_builtin_presets(SessionLocal, EffectPreset) -> None:
    """Ensure built-in effect presets exist in the database."""
    from ..utils.effects import BUILTIN_PRESETS

    db = SessionLocal()
    try:
        for idx, (_key, preset_data) in enumerate(BUILTIN_PRESETS.items()):
            sort_order = preset_data.get("sort_order", idx)
            existing = db.query(EffectPreset).filter_by(name=preset_data["name"]).first()
            if not existing:
                preset = EffectPreset(
                    id=str(uuid.uuid4()),
                    name=preset_data["name"],
                    description=preset_data.get("description"),
                    effects_chain=json.dumps(preset_data["effects_chain"]),
                    is_builtin=True,
                    sort_order=sort_order,
                )
                db.add(preset)
            elif existing.sort_order != sort_order:
                existing.sort_order = sort_order
        db.commit()
    finally:
        db.close()

def seed_jfk_profile(SessionLocal, VoiceProfile, ProfileSample) -> None:
    db = SessionLocal()
    try:
        jfk_profile = db.query(VoiceProfile).filter_by(name="JFK").first()
        if jfk_profile:
            return

        jfk_id = str(uuid.uuid4())
        jfk_profile = VoiceProfile(
            id=jfk_id,
            name="JFK",
            description="John F. Kennedy",
            language="en",
            voice_type="cloned",
            default_engine="chatterbox_turbo",
        )
        db.add(jfk_profile)

        sample_id = str(uuid.uuid4())
        assets_dir = config.get_data_dir() / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Copy our downloaded clip to the profiles dir
        profiles_dir = config.get_profiles_dir() / jfk_id
        profiles_dir.mkdir(parents=True, exist_ok=True)
        dest_path = profiles_dir / f"{sample_id}.wav"

        # Resolve path relative to this script for non-docker deployments
        src_path = os.path.join(os.path.dirname(__file__), "..", "assets", "jfk_moon_clip.wav")
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)

            sample = ProfileSample(
                id=sample_id,
                profile_id=jfk_id,
                audio_path=config.to_storage_path(dest_path),
                reference_text="We choose to go to the moon in this decade and do the other things, not because they are easy, but because they are hard",
            )
            db.add(sample)
            db.commit()
            logger.info("Seeded JFK voice profile.")

        profiles_to_seed = [
            {"name": "Accent Male", "file": "Accent Male.mp3"},
            {"name": "Angry Female", "file": "Angry Female.mp3"},
            {"name": "Angry Male", "file": "Angry Male.mp3"}
        ]

        for p in profiles_to_seed:
            existing = db.query(VoiceProfile).filter_by(name=p["name"]).first()
            if not existing:
                src_path = config.get_data_dir() / "profiles" / p["file"]
                if src_path.exists():
                    p_id = str(uuid.uuid4())
                    profile = VoiceProfile(
                        id=p_id,
                        name=p["name"],
                        description=f"{p['name']} voice sample",
                        language="en",
                        voice_type="cloned",
                        default_engine="chatterbox_turbo",
                    )
                    db.add(profile)

                    p_profiles_dir = config.get_profiles_dir() / p_id
                    p_profiles_dir.mkdir(parents=True, exist_ok=True)
                    s_id = str(uuid.uuid4())
                    p_dest_path = p_profiles_dir / f"{s_id}.mp3"
                    shutil.copy(src_path, p_dest_path)

                    p_sample = ProfileSample(
                        id=s_id,
                        profile_id=p_id,
                        audio_path=config.to_storage_path(p_dest_path),
                        reference_text=p["name"] + " sample text",
                    )
                    db.add(p_sample)
                    db.commit()
                    logger.info(f"Seeded {p['name']} voice profile.")

    except Exception as e:
        logger.error(f"Error seeding JFK profile: {e}")
        db.rollback()
    finally:
        db.close()
