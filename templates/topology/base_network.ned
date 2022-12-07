package topology;

import modules.*;
import modules.Backend.Backend;
import modules.Logger.Logger;
import channels.*;

network linear_network
{
    parameters:
        string connectionType; // MM / MIM / MSM
        int numNodes = default(5);
        int numRepeaters = numNodes - 2;
        int lastRepeaterIndex = numRepeaters - 1;
        int numHOMs = connectionType == "MIM" ? numRepeaters + 1: 0;
        double classicalDistance @unit(km) = default(1.0km);
        double quantumDistance @unit(km) = default(1.0km);

    submodules:
        backend: Backend;
        logger: Logger;
        Repeater[numNodes - 2]: QNode {
            address = index + 2;
            @display("i=device/smallrouter");
        }
        EndNode[2]: QNode {
            address = index;
            node_type = "EndNode";
            @display("i=device/pc");
        }
    	HOM[numHOMs]: HOM {
    	    address = index + parent.numNodes;
    	    @display("i=device/device");
    	}

    connections:

        if connectionType == "MIM" {
            EndNode[0].port++ <--> ClassicalChannel{distance = parent.classicalDistance / 2;} <--> HOM[0].port++;
            HOM[0].port++ <--> ClassicalChannel{distance = parent.classicalDistance / 2;} <--> Repeater[0].port++;
            EndNode[0].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance / 2;} <--> HOM[0].quantum_port++;
            HOM[0].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance / 2;} <--> Repeater[0].quantum_port++;

            Repeater[i].port++ <--> ClassicalChannel{distance = parent.classicalDistance / 2;} <--> HOM[i+1].port++ for i=0..numRepeaters - 2;
            HOM[i+1].port++ <--> ClassicalChannel{distance = parent.classicalDistance / 2;} <--> Repeater[i+1].port++ for i=0..numRepeaters - 2;
            Repeater[i].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance / 2;} <--> HOM[i+1].quantum_port++ for i=0..numRepeaters - 2;
            HOM[i+1].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance / 2;} <--> Repeater[i+1].quantum_port++ for i=0..numRepeaters - 2;

            EndNode[1].port++ <--> ClassicalChannel{distance = parent.classicalDistance / 2;} <--> HOM[sizeof(HOM)-1].port++;
            HOM[sizeof(HOM)-1].port++ <--> ClassicalChannel{distance = parent.classicalDistance / 2;} <--> Repeater[lastRepeaterIndex].port++;

            EndNode[1].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance / 2;} <--> HOM[sizeof(HOM)-1].quantum_port++;
            HOM[sizeof(HOM)-1].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance / 2;} <--> Repeater[lastRepeaterIndex].quantum_port++;

        }

        if connectionType == "MM" {
            EndNode[0].port++ <--> ClassicalChannel{distance = parent.classicalDistance;} <--> Repeater[0].port++;
            EndNode[0].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance;} <--> Repeater[0].quantum_port++;

            Repeater[i].port++ <--> ClassicalChannel{distance = parent.classicalDistance;} <--> Repeater[i+1].port++ for i=0..numRepeaters - 2;
            Repeater[i].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance;} <--> Repeater[i+1].quantum_port++ for i=0..numRepeaters - 2;

            EndNode[1].port++ <--> ClassicalChannel{distance = parent.classicalDistance;} <--> Repeater[lastRepeaterIndex].port++;
            EndNode[1].quantum_port++ <--> QuantumChannel{ distance = parent.quantumDistance;} <--> Repeater[lastRepeaterIndex].quantum_port++;
        }
}
