class SatoriCli < Formula
  include Language::Python::Virtualenv

  desc "Real-time multilingual transcription and translation with GPU acceleration"
  homepage "https://github.com/KunalKatariya/satori-cli"
  url "https://github.com/KunalKatariya/satori-cli/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "940144653281d4f4a4a8610629ceb56ef039476d129ce332495da847863f8fc9"
  license "MIT"
  version "0.1.0"

  depends_on "python@3.11"
  depends_on "portaudio"
  depends_on "ffmpeg"

  def install
    # Create a virtual environment
    virtualenv_install_with_resources
  end

  def caveats
    <<~EOS
      Satori CLI has been installed!

      First-time setup:
        1. Run: satori init
           This will download and set up whisper.cpp with Metal GPU acceleration.

        2. Install BlackHole for audio capture:
           brew install blackhole-2ch

        3. Configure audio routing:
           - Open Audio MIDI Setup
           - Create a Multi-Output Device with your speakers + BlackHole
           - In Satori settings, select BlackHole as input device

      Usage examples:
        # Real-time transcription
        satori transcribe

        # With translation (Japanese → English)
        satori transcribe --translate --target-lang en

        # Configure settings
        satori config

      For more information, visit:
        https://github.com/KunalKatariya/satori-cli
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/satori --version")
    assert_match "Usage:", shell_output("#{bin}/satori --help")
  end
end
