fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Compilar proto
    tonic_build::compile_protos("../../proto/agent.proto")?;
    Ok(())
}
