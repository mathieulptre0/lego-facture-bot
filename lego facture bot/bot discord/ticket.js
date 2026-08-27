const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, ChannelType, PermissionFlagsBits, AttachmentBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('ticket')
        .setDescription('Ouvre un nouveau ticket de support'),

    async execute(interaction) {
        const requiredRoleId = '1531392863336923246';
        const targetChannelId = '1531397308753645648';

        const botName = interaction.client.user.username;
        const botAvatar = interaction.client.user.displayAvatarURL();
        const currentDate = new Date().toLocaleDateString('fr-FR');

        if (!interaction.member.roles.cache.has(requiredRoleId)) {
            const errorEmbed = new EmbedBuilder()
                .setDescription('## ⛔ __Permission refusée__\n\nVous n\'avez pas la **permission** d\'utiliser cette commande car il vous **manque le rôle requis**.')
                .setColor(0xFF0000)
                .setFooter({ text: `${botName} — ${currentDate}`, iconURL: botAvatar });

            return await interaction.reply({ embeds: [errorEmbed], ephemeral: true });
        }

        const targetChannel = interaction.guild.channels.cache.get(targetChannelId);
        
        if (!targetChannel) {
            const channelErrorEmbed = new EmbedBuilder()
                .setDescription('## ⛔ __Erreur de configuration__\n\nLe **salon de destination** est introuvable.')
                .setColor(0xFF0000)
                .setFooter({ text: `${botName} — ${currentDate}`, iconURL: botAvatar });

            return await interaction.reply({ embeds: [channelErrorEmbed], ephemeral: true });
        }

        const embed = new EmbedBuilder()
            .setDescription(
                '### 🏥 **__Bienvenue au service d\'accueil et d\'information des EMS__ !**\n\n' +
                'Vous souhaitez **déposer une réclamation**, **poser une question** à la direction, ou **obtenir des renseignements** sur nos services ? Vous êtes au **bon endroit**.\n\n' +
                '### 📌 **__Comment faire__ ?**\n\n' +
                'Cliquez simplement sur le **bouton ci-dessous** pour **ouvrir un canal de discussion privé** avec notre équipe.\n\n' +
                '### ⚠️ **__Tout abus ou faux ticket entraînera des sanctions administratives__**'
            )
            .setColor(0x0074FF)
            .setFooter({ text: `${botName} — ${currentDate}`, iconURL: botAvatar });

        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('create_ticket')
                    .setLabel('Ouvrir un ticket')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('🎫'),
            );

        await targetChannel.send({ embeds: [embed], components: [row] });

        const successEmbed = new EmbedBuilder()
            .setDescription(`## ✅ __Succès de l'envoi__\n\nLe **panneau de tickets** a été **envoyé avec succès** dans le salon <#${targetChannelId}> !`)
            .setColor(0x00FF00)
            .setFooter({ text: `${botName} — ${currentDate}`, iconURL: botAvatar });

        await interaction.reply({ embeds: [successEmbed], ephemeral: true });
    },

    async handleInteraction(interaction) {
        if (!interaction.isButton()) return;

        const botName = interaction.client.user.username;
        const botAvatar = interaction.client.user.displayAvatarURL();
        const currentDate = new Date().toLocaleDateString('fr-FR');

        const staffRoleId = '1531400982817280020';
        const categoryId = '1531397916122415144'; 
        const transcriptChannelId = '1531405614373408778';

        if (interaction.customId === 'create_ticket') {
            const guild = interaction.guild;
            const member = interaction.member;
            const channelName = `ticket-${member.user.username.toLowerCase().replace(/[^a-z0-9]/g, '')}`;

            const existingChannel = guild.channels.cache.find(c => c.name === channelName && c.parentId === categoryId);
            if (existingChannel) {
                return await interaction.reply({
                    content: `Vous possédez déjà un ticket ouvert : <#${existingChannel.id}>`,
                    ephemeral: true
                });
            }

            const ticketChannel = await guild.channels.create({
                name: channelName,
                type: ChannelType.GuildText,
                parent: categoryId,
                permissionOverwrites: [
                    {
                        id: guild.id,
                        deny: [PermissionFlagsBits.ViewChannel],
                    },
                    {
                        id: member.id,
                        allow: [
                            PermissionFlagsBits.ViewChannel,
                            PermissionFlagsBits.SendMessages,
                            PermissionFlagsBits.ReadMessageHistory
                        ],
                    },
                    {
                        id: staffRoleId,
                        allow: [
                            PermissionFlagsBits.ViewChannel,
                            PermissionFlagsBits.SendMessages,
                            PermissionFlagsBits.ReadMessageHistory
                        ],
                    },
                ],
            });

            const closeRow = new ActionRowBuilder()
                .addComponents(
                    new ButtonBuilder()
                        .setCustomId('close_ticket')
                        .setLabel('Fermer')
                        .setStyle(ButtonStyle.Danger)
                        .setEmoji('🔒')
                );

            const welcomeEmbed = new EmbedBuilder()
                .setDescription(
                    `## 🚨 **PILOTAGE DES URGENCES & SECRÉTARIAT MÉDICAL**\n\n` +
                    `Bonjour ${member}, et bienvenue au **Pôle Médical**.\n\n` +
                    `Un **agent de l'équipe médicale** a bien reçu votre demande d'ouverture de dossier et va prendre en charge votre situation dans les plus brefs délais.`
                )
                .setColor(0x0074FF)
                .setFooter({ text: `${botName} — ${currentDate}`, iconURL: botAvatar });

            await ticketChannel.send({
                content: `${member} <@&${staffRoleId}>`,
                embeds: [welcomeEmbed],
                components: [closeRow]
            });

            await interaction.reply({
                content: `Votre ticket a été créé ici : <#${ticketChannel.id}>`,
                ephemeral: true
            });
        } 
        
        else if (interaction.customId === 'close_ticket') {
            const channel = interaction.channel;
            const guild = interaction.guild;

            await interaction.deferReply();

            const messages = await channel.messages.fetch({ limit: 100 });
            const sortedMessages = Array.from(messages.values()).reverse();

            let transcriptText = '——— TRANSCRIPTION DU TICKET ———\n\n';
            let messageCount = 0;

            for (const msg of sortedMessages) {
                if (msg.author.bot) continue;

                const authorName = msg.author.tag;
                const timestamp = msg.createdAt.toLocaleString('fr-FR');
                let content = msg.content;

                if (msg.attachments.size > 0) {
                    content += content ? ' [IMAGE]' : '[IMAGE]';
                }

                if (content.trim() !== '') {
                    transcriptText += `${authorName} | ${timestamp} : ${content}\n\n`;
                    messageCount++;
                }
            }

            if (messageCount === 0) {
                transcriptText += "Aucun message n'a été envoyé dans ce ticket.\n\n";
            }

            const buffer = Buffer.from(transcriptText, 'utf-8');
            const attachment = new AttachmentBuilder(buffer, { name: `transcript-${channel.name}.txt` });

            const transcriptChannel = guild.channels.cache.get(transcriptChannelId);
            if (transcriptChannel) {
                await transcriptChannel.send({
                    content: `Transcription du ticket fermé **${channel.name}** :`,
                    files: [attachment]
                });
            }

            const closeEmbed = new EmbedBuilder()
                .setDescription(
                    `## 🏥 **CLÔTURE DU DOSSIER MÉDICAL**\n\n` +
                    `Ce ticket est désormais **fermé**.\n\n` +
                    `Votre dossier a été archivé par le service médical. Nous espérons que votre prise en charge vous a entièrement satisfait.\n\n` +
                    `**Prenez soin de vous et restez prudents en ville !**\n` +
                    `*En cas de nouveau problème de santé ou de besoin administratif, n'hésitez pas à rouvrir un dossier.*`
                )
                .setColor(0x0074FF)
                .setFooter({ text: `${botName} — ${currentDate}`, iconURL: botAvatar });

            await channel.send({ embeds: [closeEmbed] });
            await interaction.deleteReply();

            setTimeout(async () => {
                try {
                    await channel.delete();
                } catch (e) {
                    console.error("Erreur lors de la suppression du salon du ticket :", e);
                }
            }, 5000);
        }
    }
};