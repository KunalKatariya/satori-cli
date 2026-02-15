class SatoriCli < Formula
  include Language::Python::Virtualenv

  desc "Real-time multilingual transcription and translation with GPU acceleration"
  homepage "https://github.com/KunalKatariya/satori-cli"
  license "MIT"
  head "https://github.com/KunalKatariya/satori-cli.git", branch: "main"

  depends_on "python@3.11"
  depends_on "portaudio"
  depends_on "ffmpeg"
  depends_on "poetry"

  def install
    # Create virtualenv
    venv = virtualenv_create(libexec, "python3.11")

    # Install poetry and dependencies
    system libexec/"bin/pip", "install", "--upgrade", "pip"
    system libexec/"bin/pip", "install", "poetry"

    # Install project using poetry
    cd buildpath do
      system libexec/"bin/poetry", "install", "--only", "main", "--no-root"
      system libexec/"bin/poetry", "build", "--format", "wheel"
      wheel = Dir["dist/*.whl"].first
      system libexec/"bin/pip", "install", wheel
    end

    # Create wrapper script
    (bin/"satori").write_env_script libexec/"bin/satori", PATH: "#{libexec}/bin:$PATH"
  end

  def caveats
    <<~EOS
      🎤 Satori CLI - Real-time Transcription & Translation

      Required for full functionality:

      1. whisper.cpp (GPU-accelerated transcription):
         $ satori init

      2. BlackHole (system audio capture for YouTube/Spotify):
         $ brew install blackhole-2ch

      Quick Start:
         $ satori init          # Interactive setup (installs whisper.cpp)
         $ satori devices       # List audio devices
         $ satori translate     # Start transcribing

      Examples:
         $ satori translate --loopback           # Transcribe YouTube
         $ satori translate --model large        # Better accuracy
         $ satori translate --translate-to en    # With translation

      Documentation: #{homepage}
    EOS
  end

  test do
    assert_match "Satori", shell_output("#{bin}/satori --version")
    assert_match "Usage:", shell_output("#{bin}/satori --help")
  end
end
