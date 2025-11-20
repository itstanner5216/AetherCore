# ProjectGPT

ProjectGPT is a modular skillset ecosystem designed for seamless integration into GPT projects. By zipping the project files and placing them into a GPT's project files directory, along with the appropriate project GPT instructions block, the GPT gains access to these skills automatically and intelligently. This transforms the GPT into a sophisticated modular automation system capable of executing complex, interconnected workflows.

## Overview

This repository contains a collection of autonomous skills that extend GPT capabilities through modular architecture. Each skill operates independently, while communicating via an event-driven messaging system, enabling dynamic and scalable automation.

### Key Features

- **Modular Design**: Skills can be loaded individually or in combination.
- **Event-Driven Architecture**: Skills communicate through a messaging bus and automation graph.
- **Automatic Integration**: Skills register and connect automatically upon loading.
- **Scalable Workflows**: Supports complex multi-stage automation pipelines.

## Skills Included

The repository currently includes the following skills:

### AetherCore.EventMesh
Creates a dynamic automation bridge that links event hooks and the skill messaging bus into a self-updating event graph. Enables silent, background orchestration of skill interactions.

- **Automatic Routing**: Events flow automatically between dependent skills.
- **Dynamic Updates**: Graph rebuilds when skills are loaded or unloaded.
- **Performance Optimized**: Uses cached routing tables for efficient event distribution.

### AetherCore.MarketSweep
An intelligent deal-aggregation and comparison module that searches across multiple marketplaces to find optimal product deals.

- **Exhaustive Coverage**: Searches 15+ US-based platforms including Amazon, Newegg, eBay, and more.
- **Specification Compliance**: Ensures 100% match to user requirements.
- **Real-Time Validation**: Verifies links, pricing, and availability.
- **Intelligent Ranking**: Prioritizes by compliance and total cost.

## Installation

### For GPT Project Integration

1. **Select Skills**: Choose the skills you want to integrate from the `AetherCore/` directory.
2. **Package Files**: Zip each selected skill folder (e.g., `AetherCore.EventMesh.zip`, `AetherCore.MarketSweep.zip`).
3. **Deploy to GPT**: Place the zip files into your GPT project's `project_files` directory.
4. **Configure Instructions**: Include the appropriate project GPT instructions block to enable skill loading and automation.

### Automatic Registration
Skills auto-register upon GPT session startup. No manual activation is required - the system detects and loads available skills automatically.

## Usage

Once deployed, skills become part of the GPT's capability set:

- **Automatic Activation**: Skills trigger based on context and user queries.
- **Inter-Skill Communication**: Events flow between skills to create automated workflows.
- **Background Operation**: Most automation occurs silently, with results presented seamlessly.

### Example Workflow
A user query about finding product deals might automatically trigger:
1. Query analysis and optimization
2. Deep research on requirements
3. Deal finding and comparison
4. Results presentation

## Architecture

### Core Components
- **Skill Registry**: Manages loaded skills and their metadata.
- **Messaging Bus**: Handles event routing between skills.
- **Automation Graph**: Orchestrates complex workflows and dependencies.
- **Configuration System**: Allows customization of skill behavior.

### Execution Model
Skills operate in subordinate mode, inheriting the parent GPT's context and tone while maintaining independence for their specific functions.

## Development

### Adding New Skills
1. Create a new folder in `AetherCore/`
2. Implement the skill following the universal framework spec
3. Include comprehensive documentation and configuration
4. Test integration with existing skills

### Best Practices
- Ensure skills are self-contained with minimal dependencies
- Implement proper error handling and logging
- Provide clear configuration options
- Document all events and message formats

## iOS Automation

**New!** Run ProjectGPT Prompt Factory from your iPhone or iPad:
- Use the Scriptable app for interactive prompt generation
- Integrate with iOS Shortcuts for automation workflows
- Generate prompts on-the-go without a computer

See [ios-automation/README.md](ios-automation/README.md) for setup instructions.

## Support

For issues or questions:
- Check individual skill READMEs for specific documentation
- For iOS automation issues, see [ios-automation/README.md](ios-automation/README.md)
- Verify skill placement in `project_files` directory
- Review GPT logs for loading and execution details
- Ensure compatibility with Project GPT Universal Skill Integration Framework ≥1.0

## License

This skill ecosystem is designed for use within Project GPT environments. Refer to your Project GPT license terms for usage guidelines.

---

**Note**: This system operates as an extension to GPT capabilities, enabling complex automation while maintaining the core conversational interface.