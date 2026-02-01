import csv
import json
import os
from datetime import datetime

import redis
from celery import shared_task
from sqlalchemy.exc import IntegrityError

from app import app
from app.extension import db
from app.models import Post
from config.celery import CeleryConfig

# Redis for tracking progress
r = redis.Redis.from_url(f"{CeleryConfig.REDIS_URL}/1")


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def import_posts_from_csv(self, file_path):
    """
    Import posts from CSV into the database, track progress in Redis, and handle duplicates.
    """
    batch_size = 100
    task_id = self.request.id
    errors = []

    if not os.path.exists(file_path):
        r.set(f"csv_status:{task_id}", "FAILURE")
        r.set(f"csv_errors:{task_id}", json.dumps([{"error": "File not found"}]))
        return

    with app.app_context():
        try:
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))

            total = len(reader)
            if total == 0:
                raise ValueError("CSV is empty")

            headers = [h.strip().lower() for h in reader[0].keys()]
            required_cols = ["title", "description", "status"]
            missing_cols = [col for col in required_cols if col not in headers]

            if missing_cols:
                r.set(f"csv_status:{task_id}", "FAILURE")
                r.set(
                    f"csv_errors:{task_id}",
                    json.dumps([{
                        "error": f"CSV must have columns: {', '.join(required_cols)}"
                    }])
                )
                return

            seen_titles = set()  # Track CSV duplicates

            for idx, row in enumerate(reader, 1):
                title = row["title"].strip()

                # Skip duplicates in CSV
                if title in seen_titles:
                    errors.append({"row": idx, "error": "duplicate title in CSV"})
                    continue
                seen_titles.add(title)

                # Skip duplicates in DB
                if Post.query.filter_by(title=title).first():
                    errors.append({"row": idx, "error": "duplicate title in DB"})
                    continue

                post = Post(
                    title=title,
                    description=row.get("description"),
                    status=int(row.get("status", 1)),
                    create_user_id=row.get("create_user_id"),
                    updated_user_id=row.get("updated_user_id"),
                    created_at=row.get("created_at") or datetime.utcnow(),
                    updated_at=row.get("updated_at") or datetime.utcnow(),
                )

                db.session.add(post)

                # Batch commit
                if idx % batch_size == 0:
                    try:
                        db.session.commit()
                    except IntegrityError as e:
                        db.session.rollback()
                        errors.append({"row": idx, "error": f"DB error: {str(e)}"})

                # Update progress in Redis
                progress = int((idx / total) * 100)
                r.set(f"csv_progress:{task_id}", progress)

            # Final commit for remaining posts
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                errors.append({"row": "last_batch", "error": f"DB error: {str(e)}"})

            # Save status
            if errors:
                r.set(f"csv_errors:{task_id}", json.dumps(errors))
                r.set(f"csv_status:{task_id}", "FAILURE")
            else:
                r.set(f"csv_status:{task_id}", "SUCCESS")
                r.set(f"csv_progress:{task_id}", 100)

        except Exception as e:
            db.session.rollback()
            r.set(f"csv_status:{task_id}", "FAILURE")
            r.set(f"csv_errors:{task_id}", json.dumps([{"error": str(e)}]))
            raise Exception(f"CSV import failed: {str(e)}")
