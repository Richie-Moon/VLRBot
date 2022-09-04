import discord
from discord import app_commands, ui


# https://vlrggapi.vercel.app/#/default/VLR_scores_match_results_get
guild = discord.Object(id=716770439862681620)

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=guild)
            self.synced = True
        print(f"Logged in as {self.user}")


class Questionnaire(ui.Modal, title="Questionnaire"):
    name = ui.TextInput(label='Name')
    answer = ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your response,'
                                                f' {self.name}!',
                                                ephemeral=True)


class Dropdown(ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label='Option 1'),
                   discord.SelectOption(label="Option 2"),
                   discord.SelectOption(label="Option 3")]
        super().__init__(placeholder="Select", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(content=f"Your choice is {self.values[0]}!")


class SelectView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Dropdown())


client = aclient()
tree = app_commands.CommandTree(client)


@tree.command(guild=guild)
async def test(interaction: discord.Interaction, number: int, string: str):
    await interaction.response.send_message(f'{number=} {string=}',
                                            ephemeral=False)


@tree.command(guild=guild)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f'{round(client.latency * 1000)}ms')


@tree.command(guild=guild)
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(Questionnaire())


@tree.command(guild=guild)
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(view=SelectView())


client.run(
    'MTAxNTIzNzAxMTgzNTE5MTM4Ng.Gkx736.pp7llE5PILlVGIYKUYt9hllNUUCPO38jtGS4YU')
