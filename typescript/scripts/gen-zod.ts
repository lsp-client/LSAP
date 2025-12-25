import { jsonSchemaToZod } from "json-schema-to-zod";
import { readdir, readFile, writeFile, mkdir } from "node:fs/promises";
import { join, basename } from "node:path";
import $RefParser from "@apidevtools/json-schema-ref-parser";

async function processDir(dir: string, outputDir: string) {
  const entries = await readdir(dir, { withFileTypes: true });
  const jsonFiles: string[] = [];

  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      await processDir(fullPath, join(outputDir, entry.name));
    } else if (entry.isFile() && entry.name.endsWith(".json")) {
      jsonFiles.push(entry.name);
    }
  }

  if (jsonFiles.length === 0) {
    return;
  }

  await mkdir(outputDir, { recursive: true });

  const exports = jsonFiles
    .map((name) => basename(name, ".json"))
    .sort()
    .map((name) => `export * from "./${name}";`);
  const indexContent = exports.join("\n") + "\n";
  await writeFile(join(outputDir, "index.ts"), indexContent);
  console.log(`Generated index.ts for ${outputDir}`);

  for (const fileName of jsonFiles) {
    const fullPath = join(dir, fileName);
    const rawContent = await readFile(fullPath, "utf-8");
    const rawSchema = JSON.parse(rawContent);

    const dereferencedSchema = await $RefParser.dereference(rawSchema);

    const name = basename(fileName, ".json");
    const zodCode = jsonSchemaToZod(dereferencedSchema);

    const { markdown } = dereferencedSchema as any;
    const templates = markdown ? { markdown } : undefined;
    console.log(`Checking templates for ${name}:`, templates);
    const templatesCode = templates
      ? `\n\nexport const ${name}Templates = ${JSON.stringify(templates, null, 2)} as const;`
      : "";

    const fileContent = `import { z } from "zod";

export const ${name} = ${zodCode};${templatesCode}
`;

    await writeFile(join(outputDir, `${name}.ts`), fileContent);
    console.log(`Generated Zod schema for ${name}`);
  }
}

const schemasDir = join(import.meta.dir, "../schemas");
const outputDir = join(import.meta.dir, "../src/schema");

await processDir(schemasDir, outputDir).catch(err => {
  console.error(err);
  process.exit(1);
});
