import { jsonSchemaToZod } from "json-schema-to-zod";
import { readdir, readFile, writeFile, mkdir } from "node:fs/promises";
import { join, basename } from "node:path";
import $RefParser from "@apidevtools/json-schema-ref-parser";

async function processDir(dir: string, outputDir: string) {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      await processDir(fullPath, join(outputDir, entry.name));
    } else if (entry.isFile() && entry.name.endsWith(".json")) {
      const rawContent = await readFile(fullPath, "utf-8");
      const rawSchema = JSON.parse(rawContent);
      
      // Resolve references
      const dereferencedSchema = await $RefParser.dereference(rawSchema);
      
      const name = basename(entry.name, ".json");
      const zodCode = jsonSchemaToZod(dereferencedSchema);

      const templates = (dereferencedSchema as any).lsap_templates;
      console.log(`Checking templates for ${name}:`, templates);
      const templatesCode = templates ? `\n\nexport const ${name}Templates = ${JSON.stringify(templates, null, 2)} as const;` : "";

      const fileContent = `import { z } from "zod";

export const ${name} = ${zodCode};${templatesCode}
`;

      
      await mkdir(outputDir, { recursive: true });
      await writeFile(join(outputDir, `${name}.ts`), fileContent);
      console.log(`Generated Zod schema for ${name}`);
    }
  }
}

const schemasDir = join(import.meta.dir, "../schemas");
const outputDir = join(import.meta.dir, "../src/schema");

await processDir(schemasDir, outputDir).catch(err => {
  console.error(err);
  process.exit(1);
});
