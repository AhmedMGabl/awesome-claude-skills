---
name: discord-bot
description: Discord bot development with Discord.js v14 covering slash commands, event handling, embeds, buttons, select menus, modals, permissions, database integration, and deployment patterns.
---

# Discord Bot Development

This skill should be used when building Discord bots with Discord.js v14. It covers client setup, slash command registration, interaction and event handling, rich UI components, permission guards, database persistence, and production deployment with PM2 or Docker.

## When to Use This Skill

- Set up a Discord.js v14 client with gateway intents and load commands/events dynamically
- Register slash commands via Discord's REST API (guild-scoped or global)
- Handle `interactionCreate`, `guildMemberAdd`, and other gateway events
- Build embeds with buttons, select menus, and collect modal form submissions
- Guard commands with permission or role checks
- Persist guild data with Prisma or Drizzle
- Deploy to production with PM2 or Docker

## Client Setup and Gateway Intents

```typescript
// src/index.ts
import { Client, GatewayIntentBits, Partials, Collection } from "discord.js";
export const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,   // privileged – enable in Dev Portal
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent, // privileged – enable in Dev Portal
  ],
  partials: [Partials.Channel],
});

declare module "discord.js" {
  interface Client { commands: Collection<string, SlashCommand> }
}

client.commands = new Collection();
await loadCommands(client);
await loadEvents(client);
await client.login(process.env.DISCORD_TOKEN);
```

## Slash Command Registration

Run `deploy-commands.ts` once to push commands. Use guild-scoped registration during development for instant updates; use `Routes.applicationCommands` for global production commands.

```typescript
// src/deploy-commands.ts
import { REST, Routes } from "discord.js";
const rest = new REST().setToken(process.env.DISCORD_TOKEN!);
await rest.put(
  Routes.applicationGuildCommands(process.env.CLIENT_ID!, process.env.GUILD_ID!),
  { body: commands }, // array of command.data.toJSON()
);
```

### Command File Shape

```typescript
// src/commands/ping.ts
import { SlashCommandBuilder, ChatInputCommandInteraction } from "discord.js";
export default {
  data: new SlashCommandBuilder()
    .setName("ping")
    .setDescription("Check bot latency"),

  async execute(interaction: ChatInputCommandInteraction) {
    const sent = await interaction.reply({ content: "Pinging...", fetchReply: true });
    const ms = sent.createdTimestamp - interaction.createdTimestamp;
    await interaction.editReply(`Pong! Latency: **${ms}ms** | API: **${interaction.client.ws.ping}ms**`);
  },
};
```

## Event Handlers

```typescript
// src/events/ready.ts
import { Events, Client, ActivityType } from "discord.js";
export default {
  name: Events.ClientReady, once: true,
  execute(client: Client<true>) {
    client.user.setActivity("your commands", { type: ActivityType.Listening });
    console.log(`Logged in as ${client.user.tag}`);
  },
};

// src/events/interactionCreate.ts
import { Events, Interaction } from "discord.js";
export default {
  name: Events.InteractionCreate,
  async execute(interaction: Interaction) {
    if (!interaction.isChatInputCommand()) return;
    const command = (interaction.client as any).commands.get(interaction.commandName);
    if (!command) return;
    try {
      await command.execute(interaction);
    } catch (err) {
      const msg = { content: "An error occurred.", ephemeral: true };
      interaction.replied || interaction.deferred
        ? await interaction.followUp(msg) : await interaction.reply(msg);
    }
  },
};

// src/events/guildMemberAdd.ts
import { Events, GuildMember, EmbedBuilder } from "discord.js";
export default {
  name: Events.GuildMemberAdd,
  async execute(member: GuildMember) {
    const embed = new EmbedBuilder()
      .setTitle("Welcome!")
      .setDescription(`${member} joined — ${member.guild.memberCount} members total.`)
      .setColor(0x5865f2).setTimestamp();
    await member.guild.systemChannel?.send({ embeds: [embed] });
  },
};
```

## Rich Embeds with Buttons and Select Menus

```typescript
import { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, StringSelectMenuBuilder } from "discord.js";

const embed = new EmbedBuilder().setTitle("Server Info").setColor(0x5865f2);
const buttons = new ActionRowBuilder<ButtonBuilder>().addComponents(
  new ButtonBuilder().setCustomId("refresh").setLabel("Refresh").setStyle(ButtonStyle.Primary),
  new ButtonBuilder().setLabel("Discord").setURL("https://discord.com").setStyle(ButtonStyle.Link),
);
const select = new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
  new StringSelectMenuBuilder().setCustomId("category").setPlaceholder("Choose a category")
    .addOptions({ label: "Members", value: "members" }, { label: "Channels", value: "channels" }),
);

const reply = await interaction.reply({ embeds: [embed], components: [buttons, select], fetchReply: true });
const collector = reply.createMessageComponentCollector({ time: 60_000 });
collector.on("collect", async (i) => {
  await i.deferUpdate();
  if (i.isButton() && i.customId === "refresh") {
    embed.setFooter({ text: `Refreshed at ${new Date().toLocaleTimeString()}` });
    await i.editReply({ embeds: [embed] });
  }
});
collector.on("end", () => interaction.editReply({ components: [] }).catch(() => null));
```

## Modal Forms

```typescript
import { ModalBuilder, TextInputBuilder, TextInputStyle, ActionRowBuilder } from "discord.js";

const modal = new ModalBuilder().setCustomId("feedback_modal").setTitle("Feedback");
modal.addComponents(
  new ActionRowBuilder<any>().addComponents(
    new TextInputBuilder().setCustomId("subject").setLabel("Subject")
      .setStyle(TextInputStyle.Short).setRequired(true)),
  new ActionRowBuilder<any>().addComponents(
    new TextInputBuilder().setCustomId("details").setLabel("Details")
      .setStyle(TextInputStyle.Paragraph).setRequired(true)),
);
await interaction.showModal(modal);
const submitted = await interaction.awaitModalSubmit({ time: 120_000 }).catch(() => null);
if (!submitted) return;
await submitted.reply({ content: `Received: **${submitted.fields.getTextInputValue("subject")}**`, ephemeral: true });
```

## Permission Checks and Guards

```typescript
// src/utils/guards.ts
import { ChatInputCommandInteraction, PermissionFlagsBits, GuildMember } from "discord.js";

export async function requirePermission(
  interaction: ChatInputCommandInteraction,
  permission: bigint,
): Promise<boolean> {
  if (!(interaction.member as GuildMember).permissions.has(permission)) {
    await interaction.reply({ content: "You lack permission to run this.", ephemeral: true });
    return false;
  }
  return true;
}

// In a command:
// if (!await requirePermission(interaction, PermissionFlagsBits.BanMembers)) return;
```

## Database Integration

Use Prisma (or Drizzle) to persist guild state such as warnings, user settings, and custom prefixes.

```typescript
// prisma/schema.prisma
// model Warning {
//   id        String   @id @default(cuid())
//   guildId   String
//   userId    String
//   reason    String
//   createdAt DateTime @default(now())
// }

// src/lib/db.ts
import { PrismaClient } from "@prisma/client";
export const db = new PrismaClient();

// In a command:
// await db.warning.create({ data: { guildId, userId, reason } });
// await db.warning.findMany({ where: { guildId, userId } });
```

## Deployment

### PM2

```bash
npm run build                       # compiles TypeScript to dist/
pm2 start dist/index.js --name bot
pm2 save && pm2 startup
```

### Docker

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
ENV NODE_ENV=production
CMD ["node", "dist/index.js"]
```

Pair with `docker-compose.yml` for a Postgres sidecar: add a `db` service with `image: postgres:16-alpine` and connect via `DATABASE_URL`.

## Required Environment Variables

```env
DISCORD_TOKEN=    # Bot token from Discord Developer Portal
CLIENT_ID=        # Application ID
GUILD_ID=         # Development guild (omit for global commands)
DATABASE_URL=     # PostgreSQL or SQLite connection string
```
