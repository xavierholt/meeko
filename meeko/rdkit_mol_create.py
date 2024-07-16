#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Meeko
#


from rdkit import Chem
from rdkit.Geometry import Point3D
from rdkit.Chem import AllChem
from io import StringIO
import json
import os


class RDKitMolCreate:

    ambiguous_flexres_choices = {
        "HIS": ["HIE", "HID", "HIP"],
        "ASP": ["ASP", "ASH"],
        "GLU": ["GLU", "GLH"],
        "CYS": ["CYS", "CYM"],
        "LYS": ["LYS", "LYN"],
        "ARG": ["ARG", "ARG_mgltools"],
        "ASN": ["ASN", "ASN_mgltools"],
        "GLN": ["GLN", "GLN_mgltools"],
    }

    flexres = {
        "CYS": {
            "smiles": "CCS",
            "atom_names_in_smiles_order": ["CA", "CB", "SG"],
            "h_to_parent_index": {"HG": 2},
        },
        "CYM": {
            "smiles": "CC[S-]",
            "atom_names_in_smiles_order": ["CA", "CB", "SG"],
            "h_to_parent_index": {},
        },
        "ASP": {
            "smiles": "CCC(=O)[O-]",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "OD1", "OD2"],
            "h_to_parent_index": {},
        },
        "ASH": {
            "smiles": "CCC(=O)O",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "OD1", "OD2"],
            "h_to_parent_index": {"HD2": 4},
        },
        "GLU": {
            "smiles": "CCCC(=O)[O-]",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD", "OE1", "OE2"],
            "h_to_parent_index": {},
        },
        "GLH": {
            "smiles": "CCCC(=O)O",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD", "OE1", "OE2"],
            "h_to_parent_index": {"HE2": 5},
        },
        "PHE": {
            "smiles": "CCc1ccccc1",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD1", "CE1", "CZ", "CE2", "CD2"],
            "h_to_parent_index": {},
        },
        "HIE" : {
            "smiles": "CCc1c[nH]cn1",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD2", "NE2", "CE1", "ND1"],
            "h_to_parent_index": {"HE2": 4},
        },
        "HID" : {
            "smiles": "CCc1cnc[nH]1",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD2", "NE2", "CE1", "ND1"],
            "h_to_parent_index": {"HD1": 6},
        },
        "HIP" : {
            "smiles": "CCc1c[nH+]c[nH]1",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD2", "NE2", "CE1", "ND1"],
            "h_to_parent_index": {"HE2": 4, "HD1": 6},
        },
        "ILE": {
            "smiles": "CC(C)CC",
            "atom_names_in_smiles_order": ["CA", "CB", "CG2", "CG1", "CD1"],
            "h_to_parent_index": {},
        },
        "LYS": {
            "smiles": "CCCCC[NH3+]",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD", "CE", "NZ"],
            "h_to_parent_index": {"HZ1": 5, "HZ2": 5, "HZ3": 5},
        },
        "LYN": {
            "smiles": "CCCCCN",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD", "CE", "NZ"],
            "h_to_parent_index": {"HZ2": 5, "HZ3": 5},
        },
        "LEU": {
            "smiles": "CCC(C)C",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD1", "CD2"],
            "h_to_parent_index": {},
        },
        "MET": {
            "smiles": "CCCSC",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "SD", "CE"],
            "h_to_parent_index": {},
        },
        "ASN": {
            "smiles": "CCC(=O)N",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "OD1", "ND2"],
            "h_to_parent_index": {"HD21": 4, "HD22": 4},
        },
        "ASN_mgltools": {
            "smiles": "CCC(=O)N",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "OD1", "ND2"],
            "h_to_parent_index": {"1HD2": 4, "2HD2": 4},
        },
        "GLN": {
            "smiles": "CCCC(=O)N",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD", "OE1", "NE2"],
            "h_to_parent_index": {"HE21": 5, "HE22": 5},
        },
        "GLN_mgltools": {
            "smiles": "CCCC(=O)N",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD", "OE1", "NE2"],
            "h_to_parent_index": {"1HE2": 5, "2HE2": 5},
        },
        "ARG": {
            "smiles": "CCCCNC(N)=[NH2+]",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD", "NE", "CZ", "NH1", "NH2"],
            "h_to_parent_index": {"HE": 4, "HH11": 6, "HH12": 6, "HH21": 7, "HH22": 7},
        },
        "ARG_mgltools": {
            "smiles": "CCCCNC(N)=[NH2+]",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD", "NE", "CZ", "NH1", "NH2"],
            "h_to_parent_index": {"HE": 4, "1HH1": 6, "2HH1": 6, "1HH2": 7, "2HH2": 7},
        },
        "SER": {
            "smiles": "CCO",
            "atom_names_in_smiles_order": ["CA", "CB", "OG"],
            "h_to_parent_index": {"HG": 2},
        },
        "THR": {
            "smiles": "CC(C)O",
            "atom_names_in_smiles_order": ["CA", "CB", "CG2", "OG1"],
            "h_to_parent_index": {"HG1": 3},
        },
        "VAL": {
            "smiles": "CC(C)C",
            "atom_names_in_smiles_order": ["CA", "CB", "CG1", "CG2"],
            "h_to_parent_index": {},
        },
        "TRP": {
            "smiles": "CCc1c[nH]c2c1cccc2",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD1", "NE1", "CE2", "CD2", "CE3", "CZ3", "CH2", "CZ2"],
            "h_to_parent_index": {"HE1": 4},
        },
        "TYR": {
            "smiles": "CCc1ccc(cc1)O",
            "atom_names_in_smiles_order": ["CA", "CB", "CG", "CD1", "CE1", "CZ", "CE2", "CD2", "OH"],
            "h_to_parent_index": {"HH": 8},
        },
    }

    @classmethod
    def from_pdbqt_mol(cls, pdbqt_mol, only_cluster_leads=False): # TODO add pseudo-water (W atoms, variable nr each pose)
        if only_cluster_leads and len(pdbqt_mol._pose_data["cluster_leads_sorted"]) == 0:
            raise RuntimeError("no cluster_leads in pdbqt_mol but only_cluster_leads=True")
        mol_list = []
        for mol_index in pdbqt_mol._atom_annotations["mol_index"]:
            smiles = pdbqt_mol._pose_data['smiles'][mol_index]
            index_map = pdbqt_mol._pose_data['smiles_index_map'][mol_index]
            h_parent = pdbqt_mol._pose_data['smiles_h_parent'][mol_index]
            atom_idx = pdbqt_mol._atom_annotations["mol_index"][mol_index]

            if smiles is None: # probably a flexible sidechain, but can be another ligand
                residue_names = set()
                atom_names = []
                for atom in pdbqt_mol.atoms(atom_idx):
                    residue_names.add(atom[4])
                    atom_names.append(atom[2])
                if len(residue_names) == 1:
                    resname = residue_names.pop()
                    smiles, index_map, h_parent = cls.guess_flexres_smiles(resname, atom_names)
                    if smiles is None: # failed guessing smiles for possible flexres
                        mol_list.append(None)
                        continue

            if only_cluster_leads:
                pose_ids = pdbqt_mol._pose_data["cluster_leads_sorted"]
            else:
                pose_ids = range(pdbqt_mol._pose_data["n_poses"])

            mol = Chem.MolFromSmiles(smiles)
            coordinates_all_poses = []
            for i in pose_ids:
                pdbqt_mol._current_pose = i
                coordinates = pdbqt_mol.positions(atom_idx)
                mol = cls.add_pose_to_mol(mol, coordinates, index_map) 
                coordinates_all_poses.append(coordinates) 

            # add Hs only after all poses are added as conformers
            # because Chem.AddHs() will affect all conformers at once 
            mol = cls.add_hydrogens(mol, coordinates_all_poses, h_parent) 

            mol_list.append(mol)
        return mol_list

    @classmethod
    def guess_flexres_smiles(cls, resname, atom_names):
        """ Determine a SMILES string for flexres based on atom names,
            as well as the equivalent of smile_index_map and smiles_h_parent
            which are written to PDBQT remarks for regular small molecules.

        Args:
            resname (str):
        
        Returns:
            smiles: SMILES string starting at C-alpha (excludes most of the backbone)
            index_map: list of pairs of integers, first in pair is index in the smiles,
                       second is index of corresponding atom in atom_names         
            h_parent: list of pairs of integers, first in pair is index of a heavy atom
                      in the smiles, second is index of a hydrogen in atom_names.
                      The hydrogen is bonded to the heavy atom. 
        """



        if len(set(atom_names)) != len(atom_names):
            return None, None, None
        candidate_resnames = cls.ambiguous_flexres_choices.get(resname, [resname])
        for resname in candidate_resnames:
            is_match = False
            if resname not in cls.flexres[resname]["atom_names_in_smiles_order"]:
                continue
            atom_names_in_smiles_order = cls.flexres[resname]["atom_names_in_smiles_order"]
            h_to_parent_index = cls.flexres[resname]["h_to_parent_index"]
            expected_names = atom_names_in_smiles_order + list(h_to_parent_index.keys())
            if len(atom_names) != len(expected_names):
                continue
            nr_matched_atom_names = sum([int(n in atom_names) for n in expected_names])
            if nr_matched_atom_names == len(expected_names):
                is_match = True
                break
        if not is_match:
            return None, None, None
        else:
            smiles = cls.flexres[resname]["smiles"]
            index_map = []
            for smiles_index, name in enumerate(atom_names_in_smiles_order):
                index_map.append(smiles_index + 1) 
                index_map.append(atom_names.index(name) + 1)
            h_parent = []
            for name, smiles_index in h_to_parent_index.items():
                h_parent.append(smiles_index + 1)
                h_parent.append(atom_names.index(name) + 1)
            return smiles, index_map, h_parent

    @classmethod
    def add_pose_to_mol(cls, mol, ligand_coordinates, index_map):
        """add given coordinates to given molecule as new conformer.
        Index_map maps order of coordinates to order in smile string
        used to generate rdkit mol

        Args:
            ligand_coordinates: 2D array of shape (nr_atom, 3).
            index_map: list of nr_atom pairs of integers, 1-indexed.
                       In each pair, the first int is the index in mol, and
                       the second int is the index in ligand_coordinates

        Raises:
            RuntimeError: Will raise error if number of coordinates provided does not
                match the number of atoms there should be coordinates for.
        """

        n_atoms = mol.GetNumAtoms()
        n_mappings = int(len(index_map) / 2)
        conf = Chem.Conformer(n_atoms)
        if n_atoms < n_mappings:
            raise RuntimeError(
                "Given {n_coords} atom coordinates "
                "but index_map is greater at {n_at} atoms.".format(
                    n_coords=n_atoms, n_at=n_mappings))
        coord_is_set = [False] * n_atoms
        for i in range(n_mappings):
            pdbqt_index = int(index_map[i * 2 + 1]) - 1
            mol_index = int(index_map[i * 2]) - 1
            x, y, z = [float(coord) for coord in ligand_coordinates[pdbqt_index]]
            conf.SetAtomPosition(mol_index, Point3D(x, y, z))
            coord_is_set[mol_index] = True
        mol.AddConformer(conf, assignId=True)
        # some hydrogens (isotopes) may have no coordinate set yet
        for i, is_set in enumerate(coord_is_set):
            if not is_set:
                atom = mol.GetAtomWithIdx(i)
                if atom.GetAtomicNum() != 1:
                    raise RuntimeError("Only H allowed to be in SMILES but not in PDBQT")
                neigh = atom.GetNeighbors()
                if len(neigh) != 1:
                    raise RuntimeError("Expected H to have one neighbor")
                AllChem.SetTerminalAtomCoords(mol, i, neigh[0].GetIdx())
        return mol


    @staticmethod
    def add_hydrogens(mol, coordinates_list, h_parent):
        """Add hydrogen atoms to ligand RDKit mol, adjust the positions of
            polar hydrogens to match pdbqt
        """
        mol = Chem.AddHs(mol, addCoords=True)
        conformers = list(mol.GetConformers())
        num_hydrogens = int(len(h_parent) / 2)
        for conformer_idx, atom_coordinates in enumerate(coordinates_list):
            conf = conformers[conformer_idx]
            used_h = []
            for i in range(num_hydrogens):
                parent_rdkit_index = h_parent[2 * i] - 1
                h_pdbqt_index = h_parent[2 * i + 1] - 1
                x, y, z = [
                    float(coord) for coord in atom_coordinates[h_pdbqt_index]
                ]
                parent_atom = mol.GetAtomWithIdx(parent_rdkit_index)
                candidate_hydrogens = [
                    atom.GetIdx() for atom in parent_atom.GetNeighbors()
                    if atom.GetAtomicNum() == 1
                ]
                for h_rdkit_index in candidate_hydrogens:
                    if h_rdkit_index not in used_h:
                        break
                used_h.append(h_rdkit_index)
                conf.SetAtomPosition(h_rdkit_index, Point3D(x, y, z))
        return mol

    @staticmethod
    def combine_rdkit_mols(mol_list):
        """Combines list of rdkit molecules into a single one
            None's are ignored
            returns None if input is empty list or all molecules are None
        """
        combined_mol = None
        for mol in mol_list:
            if mol is None:
                continue
            if combined_mol is None: # first iteration
                combined_mol = mol
            else:
                combined_mol = Chem.CombineMols(combined_mol, mol)
        return combined_mol

    @classmethod
    def _verify_flexres(cls):
        for resname in cls.flexres:
            atom_names_in_smiles_order = cls.flexres[resname]["atom_names_in_smiles_order"]
            h_to_parent_index = cls.flexres[resname]["h_to_parent_index"]
            expected_names = atom_names_in_smiles_order + list(h_to_parent_index.keys())
            if len(expected_names) != len(set(expected_names)):
                raise RuntimeError("repeated atom names in cls.flexres[%s]" % resname)

    @staticmethod
    def write_sd_string(pdbqt_mol, only_cluster_leads=False):
        sio = StringIO()
        f = Chem.SDWriter(sio)
        mol_list = RDKitMolCreate.from_pdbqt_mol(pdbqt_mol, only_cluster_leads)
        failures = [i for i, mol in enumerate(mol_list) if mol is None]
        combined_mol = RDKitMolCreate.combine_rdkit_mols(mol_list)
        if combined_mol is None:
            return "", failures
        nr_conformers = combined_mol.GetNumConformers()
        property_names = {
            "free_energy": "free_energies",
            "intermolecular_energy": "intermolecular_energies",
            "internal_energy": "internal_energies",
            "cluster_size": "cluster_size",
            "cluster_id": "cluster_id",
            "rank_in_cluster": "rank_in_cluster",
        }
        props = {}
        if only_cluster_leads:
            nr_poses = len(pdbqt_mol._pose_data["cluster_leads_sorted"])
            pose_idxs = pdbqt_mol._pose_data["cluster_leads_sorted"]
        else:
            nr_poses = pdbqt_mol._pose_data["n_poses"]
            pose_idxs = list(range(nr_poses))

        if nr_conformers == nr_poses:
            for prop_sdf, prop_pdbqt in property_names.items():
                if len(pdbqt_mol._pose_data[prop_pdbqt]) == nr_conformers:
                    props[prop_sdf] = pdbqt_mol._pose_data[prop_pdbqt]

        for conformer in combined_mol.GetConformers():
            i = conformer.GetId()
            j = pose_idxs[i]
            data = {k: v[j] for k, v in props.items()}
            combined_mol.SetProp("meeko", json.dumps(data))
            f.write(combined_mol, i)
        f.close()
        output_string = sio.getvalue()
        return output_string, failures
