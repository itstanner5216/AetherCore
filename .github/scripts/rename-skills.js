#!/usr/bin/env node

/**
 * AetherCore Skill Identifier Migration Script
 * 
 * This script migrates legacy skill identifiers to their canonical AetherCore names
 * across the repository. It updates file contents and renames files/directories.
 * 
 * Legacy to Canonical Mappings:
 * - knowledge-orchestrator to AetherCore.Orchestrator
 * - automation-graph to AetherCore.EventMesh
 * - optimization-profile to AetherCore.OptiGraph
 * - deep-research-extension to AetherCore.DeepForge
 * - dealfinder-extension to AetherCore.MarketSweep
 * - prompt-factory to AetherCore.PromptFoundry
 * - skill-messaging-bus to AetherCore.EventMesh
 * 
 * Features:
 * - Idempotent (safe to run multiple times)
 * - Skips .git and node_modules directories
 * - Updates content in text files
 * - Renames files and directories containing legacy identifiers
 * - Preserves file structure and formatting
 */

const fs = require('fs');
const path = require('path');

// Configuration
const LEGACY_TO_CANONICAL = {
  'knowledge-orchestrator': 'AetherCore.Orchestrator',
  'automation-graph': 'AetherCore.EventMesh',
  'optimization-profile': 'AetherCore.OptiGraph',
  'deep-research-extension': 'AetherCore.DeepForge',
  'dealfinder-extension': 'AetherCore.MarketSweep',
  'prompt-factory': 'AetherCore.PromptFoundry',
  'skill-messaging-bus': 'AetherCore.EventMesh'
};

// File extensions to process for content replacement
const TEXT_FILE_EXTENSIONS = [
  '.md', '.yaml', '.yml', '.json', '.js', '.ts', '.py', 
  '.sh', '.txt', '.html', '.css', '.scss', '.less', '.mdx'
];

// Directories to skip
const SKIP_DIRECTORIES = ['.git', 'node_modules', '.next', 'dist', 'build', 'coverage'];

// Statistics tracking
const stats = {
  filesUpdated: 0,
  filesRenamed: 0,
  directoriesRenamed: 0,
  totalReplacements: 0
};

/**
 * Check if a file is a text file based on its extension
 */
function isTextFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return TEXT_FILE_EXTENSIONS.includes(ext);
}

/**
 * Check if a directory should be skipped
 */
function shouldSkipDirectory(dirName) {
  return SKIP_DIRECTORIES.includes(dirName);
}

/**
 * Check if a path contains any legacy identifier
 */
function containsLegacyIdentifier(text) {
  return Object.keys(LEGACY_TO_CANONICAL).some(legacy => text.includes(legacy));
}

/**
 * Replace all legacy identifiers in text with canonical names
 */
function replaceIdentifiers(content) {
  let updatedContent = content;
  let replacementCount = 0;

  // Sort by length (descending) to replace longer patterns first
  const sortedLegacy = Object.keys(LEGACY_TO_CANONICAL).sort((a, b) => b.length - a.length);

  for (const legacy of sortedLegacy) {
    const canonical = LEGACY_TO_CANONICAL[legacy];
    const regex = new RegExp(legacy, 'g');
    const matches = (updatedContent.match(regex) || []).length;
    
    if (matches > 0) {
      updatedContent = updatedContent.replace(regex, canonical);
      replacementCount += matches;
    }
  }

  return { updatedContent, replacementCount };
}

/**
 * Process a single file: update its content if it's a text file
 */
function processFile(filePath) {
  if (!isTextFile(filePath)) {
    return;
  }

  // Skip the migration script and workflow file to avoid self-modification
  if (filePath.endsWith('rename-skills.js') || filePath.endsWith('update-skill-identifiers.yml')) {
    return;
  }

  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    if (!containsLegacyIdentifier(content)) {
      return; // No legacy identifiers found
    }

    const { updatedContent, replacementCount } = replaceIdentifiers(content);

    if (replacementCount > 0) {
      fs.writeFileSync(filePath, updatedContent, 'utf8');
      console.log(`✓ Updated ${filePath} (${replacementCount} replacements)`);
      stats.filesUpdated++;
      stats.totalReplacements += replacementCount;
    }
  } catch (error) {
    console.error(`✗ Error processing file ${filePath}:`, error.message);
  }
}

/**
 * Rename a file or directory if it contains legacy identifiers
 */
function renameIfNeeded(itemPath, isDirectory = false) {
  const dirname = path.dirname(itemPath);
  const basename = path.basename(itemPath);

  if (!containsLegacyIdentifier(basename)) {
    return itemPath; // No rename needed
  }

  const { updatedContent: newBasename } = replaceIdentifiers(basename);
  const newPath = path.join(dirname, newBasename);

  if (itemPath === newPath) {
    return itemPath; // No change after replacement
  }

  try {
    // Check if target already exists
    if (fs.existsSync(newPath)) {
      console.warn(`⚠ Skip rename: ${newPath} already exists`);
      return itemPath;
    }

    fs.renameSync(itemPath, newPath);
    
    if (isDirectory) {
      console.log(`✓ Renamed directory: ${basename} → ${newBasename}`);
      stats.directoriesRenamed++;
    } else {
      console.log(`✓ Renamed file: ${basename} → ${newBasename}`);
      stats.filesRenamed++;
    }
    
    return newPath;
  } catch (error) {
    console.error(`✗ Error renaming ${itemPath}:`, error.message);
    return itemPath;
  }
}

/**
 * Recursively traverse and process directory
 */
function processDirectory(dirPath) {
  let entries;
  
  try {
    entries = fs.readdirSync(dirPath, { withFileTypes: true });
  } catch (error) {
    console.error(`✗ Error reading directory ${dirPath}:`, error.message);
    return;
  }

  // First pass: process files and recurse into directories
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);

    if (entry.isDirectory()) {
      if (shouldSkipDirectory(entry.name)) {
        console.log(`⊘ Skipping directory: ${fullPath}`);
        continue;
      }
      processDirectory(fullPath);
    } else if (entry.isFile()) {
      processFile(fullPath);
    }
  }

  // Second pass: rename files and directories
  // We do this after processing to avoid path issues
  const entriesToRename = fs.readdirSync(dirPath, { withFileTypes: true });
  
  for (const entry of entriesToRename) {
    if (shouldSkipDirectory(entry.name)) {
      continue;
    }

    const fullPath = path.join(dirPath, entry.name);
    renameIfNeeded(fullPath, entry.isDirectory());
  }
}

/**
 * Main execution function
 */
function main() {
  console.log('=================================================');
  console.log('AetherCore Skill Identifier Migration');
  console.log('=================================================\n');

  console.log('Legacy to Canonical Mappings:');
  for (const [legacy, canonical] of Object.entries(LEGACY_TO_CANONICAL)) {
    console.log(`  ${legacy} to ${canonical}`);
  }
  console.log('');

  const rootDir = process.cwd();
  console.log(`Starting migration from: ${rootDir}\n`);

  processDirectory(rootDir);

  console.log('\n=================================================');
  console.log('Migration Complete');
  console.log('=================================================');
  console.log(`Files updated:        ${stats.filesUpdated}`);
  console.log(`Files renamed:        ${stats.filesRenamed}`);
  console.log(`Directories renamed:  ${stats.directoriesRenamed}`);
  console.log(`Total replacements:   ${stats.totalReplacements}`);
  console.log('=================================================\n');

  if (stats.filesUpdated === 0 && stats.filesRenamed === 0 && stats.directoriesRenamed === 0) {
    console.log('✓ No legacy identifiers found. Repository is up to date.');
  } else {
    console.log('✓ Migration completed successfully.');
  }
}

// Run the migration
if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error('✗ Migration failed:', error.message);
    process.exit(1);
  }
}

module.exports = { replaceIdentifiers, containsLegacyIdentifier };
