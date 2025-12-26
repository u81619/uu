import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
import os, shutil, zipfile, time
from io import BytesIO
from wand.image import Image as WandImage

os.environ['MAGICK_HOME'] = r"put path your image magick"

sizes = [440, 260, 128, 64]

def add_files_to_zip_in_memory(file_paths: list[str]) -> bytes:
    in_memory_zip = BytesIO()
    with zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in file_paths:
            arcname = os.path.basename(file_path)
            zf.write(file_path, arcname)
    in_memory_zip.seek(0)
    return in_memory_zip.read()

def process_image(img, temp_dir):
    img.format = "png"
    img.resize(440, 440)
    img.save(filename=os.path.join(temp_dir, "avatar.png"))
    img.compression = "dxt5"
    for size in sizes:
        if img.width != size:
            img.resize(size, size)
        img.save(filename=os.path.join(temp_dir, f"avatar{size}.dds"))

def copy_files(temp_dir, activated=False):
    online_json_content = r"""{"avatarUrl":"...","isOfficiallyVerified":%s}""" % str(activated).lower()
    with open(f"{temp_dir}/online.json", "w") as f:
        f.write(online_json_content)
    shutil.copy(f"{temp_dir}/avatar.png", f"{temp_dir}/picture.png")
    for size in sizes:
        shutil.copy(f"{temp_dir}/avatar{size}.dds", f"{temp_dir}/picture{size}.dds")

def convert_image_from_bytes(image_bytes, activated=False):
    temp_dir = "temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    start_time = time.time()
    with WandImage(blob=image_bytes) as img:
        process_image(img, temp_dir)
        copy_files(temp_dir, activated)
    file_paths = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)]
    archive_bytes = add_files_to_zip_in_memory(file_paths)
    shutil.rmtree(temp_dir)
    end_time = time.time()
    print(f"Conversion done in {end_time - start_time:.2f}s")
    return archive_bytes

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class ActivatedView(View):
    def __init__(self, image_bytes: bytes):
        super().__init__(timeout=300)
        self.image_bytes = image_bytes

    @discord.ui.button(label="Activated (Yes)", style=discord.ButtonStyle.green)
    async def activated_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Processing image (Activated)... ⏳", view=None)
        archive_bytes = convert_image_from_bytes(self.image_bytes, activated=True)
        output_file = discord.File(BytesIO(archive_bytes), filename="avatar.xavatar")
        await interaction.followup.send("XAvatar created successfully ✅ (Activated)", file=output_file)

    @discord.ui.button(label="Not Activated (No)", style=discord.ButtonStyle.grey)
    async def activated_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Processing image (Not Activated)... ⏳", view=None)
        archive_bytes = convert_image_from_bytes(self.image_bytes, activated=False)
        output_file = discord.File(BytesIO(archive_bytes), filename="avatar.xavatar")
        await interaction.followup.send("XAvatar created successfully ✅ (Not Activated)", file=output_file)

    async def on_timeout(self):
        await self.message.edit(content="Selection timeout expired ⏰", view=None)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="avatar", description="Convert an image to XAvatar")
@app_commands.describe(file="Choose an image to convert")
async def avatar(interaction: discord.Interaction, file: discord.Attachment):
    image_bytes = await file.read()
    view = ActivatedView(image_bytes)
    embed = discord.Embed(title="Convert Image to XAvatar")
    embed.description = "Is the account verified/activated? Choose from the buttons below:"
    embed.set_image(url=file.url)
    await interaction.response.send_message(embed=embed, view=view)


bot.run("put your token bot")
