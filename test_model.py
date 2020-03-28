import time
import torch as th
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from constants import *
from model import *
from torch.autograd import Variable

from torchviz import make_dot, make_dot_from_trace
import analyze_graph 

th.manual_seed(1)


# start test functions with test_
def test_example():
    pass


def test_dcn_model():
    # https://discuss.pytorch.org/t/solved-make-sure-that-pytorch-using-gpu-to-compute/4870/2
    # Is GPU available:
    print ("cuda device count = %d" % th.cuda.device_count())
    print ("cuda is available = %d" % th.cuda.is_available())
    device = th.device("cuda:0" if th.cuda.is_available() and (not DISABLE_CUDA) else "cpu")

    doc = th.randn(BATCH_SIZE, 30, EMBEDDING_DIM, device=device) # Fake word vec dimension set to EMBEDDING_DIM.
    que = th.randn(BATCH_SIZE, 5, EMBEDDING_DIM, device=device)  # Fake word vec dimension set to EMBEDDING_DIM.

    # Fake ground truth data (one batch of starts and ends):
    true_s = th.randint(0, doc.size()[1], (BATCH_SIZE,), device=device)
    true_e = th.randint(0, doc.size()[1], (BATCH_SIZE,), device=device)
    for i in range(BATCH_SIZE):
      true_s[i], true_e[i] = min(true_s[i], true_e[i]), max(true_s[i], true_e[i])

    # Run model.
    model = DCNModel(BATCH_SIZE, device).to(device)
    loss, s, e = model.forward(doc, que, true_s, true_e)
    print("Predicted start: %s \nPredicted end: %s \nloss: %s" % (str(s), str(e), str(loss)))
    model.zero_grad()
    loss.backward()

    print("%d/%d parameters have non-None gradients." % (len([param for param in model.parameters() if param.grad is not None]), len(list(model.parameters()))))


def test_hmn():
    device = th.device("cuda:0" if th.cuda.is_available() and (not DISABLE_CUDA) else "cpu")
    hmn = HighwayMaxoutNetwork(BATCH_SIZE, DROPOUT, HIDDEN_DIM, MAXOUT_POOL_SIZE, device).to(device)
    u_t = th.ones(BATCH_SIZE, 2 * HIDDEN_DIM, 1, device=device)
    h_i = th.ones(BATCH_SIZE, HIDDEN_DIM, 1, device=device)
    u_si_m_1, u_ei_m_1 = th.ones(BATCH_SIZE, 2 * HIDDEN_DIM, 1, device=device), th.ones(BATCH_SIZE, 2 * HIDDEN_DIM, 1, device=device) #TODO device
    output = hmn.forward(u_t, h_i, u_si_m_1, u_ei_m_1)

    # Call backward on a scalar ("output" is of dimension BATCH_SIZE x 1)
    assert(output.size()[0] == hmn.batch_size)
    assert(output.size()[1] == 1)
    th.mean(output).backward()
    print("%d/%d parameters have non-None gradients." % (len([param for param in hmn.parameters() if param.grad is not None]), len(list(hmn.parameters()))))


def test_decoder():
    max_iter = 10
    device = th.device("cuda:0" if th.cuda.is_available() and (not DISABLE_CUDA) else "cpu")
    dpd = DynamicPointerDecoder(BATCH_SIZE, max_iter, DROPOUT, DROPOUT, HIDDEN_DIM, MAXOUT_POOL_SIZE, device).to(device)
    U = th.ones(BATCH_SIZE, 2 * HIDDEN_DIM, 50, device=device)
    alphas, betas, s, e = dpd.forward(U)
    loss = th.mean(th.mean(alphas, dim=0)) + th.mean(th.mean(betas, dim=0))
    dpd.zero_grad()
    loss.backward()
    print(loss)


# Optimiser.
def test_optimiser():
  
    # Is GPU available:
    print ("cuda device count = %d" % th.cuda.device_count())
    print ("cuda is available = %d" % th.cuda.is_available())
    device = th.device("cuda:0" if th.cuda.is_available() and (not DISABLE_CUDA) else "cpu")

    # Fake one batch of data
    doc = th.randn(BATCH_SIZE, 30, EMBEDDING_DIM, device=device) # Fake word vec dimension set to EMBEDDING_DIM.
    que = th.randn(BATCH_SIZE, 5, EMBEDDING_DIM, device=device)  # Fake word vec dimension set to EMBEDDING_DIM.

    # Fake one batch of ground truth
    true_s = th.randint(0, doc.size()[1], (BATCH_SIZE,), device=device)
    true_e = th.randint(0, doc.size()[1], (BATCH_SIZE,), device=device)
    for i in range(BATCH_SIZE):
      true_s[i], true_e[i] = min(true_s[i], true_e[i]), max(true_s[i], true_e[i])

    model = DCNModel(BATCH_SIZE, device).to(device)

    # TODO: hyperparameters
    optimizer = optim.Adam(model.parameters())
    N_STEPS = 7

    loss_values_over_steps = []

    nodes_current = None

    for step_it in range(N_STEPS):
        optimizer.zero_grad()
        loss, _, _ = model(doc, que, true_s, true_e)
        
        dot = make_dot(loss)

        dotOutPath = "dot_output" + str(step_it) + ".dot"
        with open(dotOutPath, "w") as f:
            f.write(str(dot))

        num_distinct_nodes, new_node_ids = analyze_graph.num_distinct_node_ids(dotOutPath, debug_print=True)
        if nodes_current is not None:
            new_nodes = analyze_graph.new_nodes(nodes_current, new_node_ids)
            print("num_new_nodes", len(new_nodes))
            freed_nodes = analyze_graph.freed_nodes(nodes_current, new_node_ids)
            print("num_freed_nodes", len(freed_nodes))
            persisting_nodes = analyze_graph.persisting_nodes(nodes_current, new_node_ids)
            print("num_persisting_nodes", len(persisting_nodes))


            with open("persisting_nodes.txt", "w") as f:
                print("Writing persisting nodes to file...")
                f.write("\n".join(persisting_nodes))

        nodes_current = new_node_ids

        loss.backward(retain_graph=False)  # TODO: Should this be here?

        optimizer.step()
        loss_values_over_steps.append(loss[0])
        print("Loss after %d steps: %f" %(step_it+1, loss[0]))

    assert(loss_values_over_steps[0] >= loss_values_over_steps[-1])
    print("Optimizer finished.")
