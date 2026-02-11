const fs = require('fs-extra');
const path = require('path');
const minimist = require('minimist');
const glob = require('glob');

const args = minimist(process.argv.slice(2));
const DAYS_TO_KEEP = args.days || 3;
const LOG_DIR = args['log-dir'] || 'logs';
const ARCHIVE_DIR = args['archive-dir'] || 'logs/archive';

async function main() {
  console.log(`[Log Archiver] Starting... Keep days: ${DAYS_TO_KEEP}`);
  
  if (!fs.existsSync(LOG_DIR)) {
    console.error(`Log directory not found: ${LOG_DIR}`);
    return;
  }

  await fs.ensureDir(ARCHIVE_DIR);

  // Find task files
  const files = glob.sync(`${LOG_DIR}/task_*.txt`);
  const now = Date.now();
  let movedCount = 0;

  for (const file of files) {
    const stats = fs.statSync(file);
    const ageDays = (now - stats.mtimeMs) / (1000 * 60 * 60 * 24);

    if (ageDays > DAYS_TO_KEEP) {
      const filename = path.basename(file);
      const dest = path.join(ARCHIVE_DIR, filename);
      await fs.move(file, dest, { overwrite: true });
      movedCount++;
    }
  }

  console.log(`[Log Archiver] Archived ${movedCount} files to ${ARCHIVE_DIR}`);
}

main().catch(console.error);
